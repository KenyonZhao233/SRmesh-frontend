<template>
  <div class="telemetry-container">
    <div class="page-header">
      <h2>遥测信息（P4 灰色故障事件）</h2>
      <div class="controls">
        <el-input v-model="search" placeholder="搜索设备/切片/事件..." clearable style="width: 260px" />
        <el-select v-model="severity" placeholder="严重级别" clearable style="width: 160px">
          <el-option label="warning" value="warning" />
          <el-option label="minor" value="minor" />
          <el-option label="major" value="major" />
          <el-option label="critical" value="critical" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadEvents">刷新</el-button>
        <el-switch v-model="autoRefresh" active-text="自动刷新" />
      </div>
    </div>

    <el-card shadow="hover" class="table-card">
      <el-table :data="filtered" v-loading="loading" border style="width: 100%">
        <el-table-column prop="detected_at" label="时间" width="170" />
        <el-table-column prop="event_type" label="事件类型" width="140">
          <template #default="scope">
            <el-tag :type="typeColor(scope.row.event_type)">{{ scope.row.event_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="级别" width="110">
          <template #default="scope">
            <el-tag :type="severityColor(scope.row.severity)">{{ scope.row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="device_name" label="设备" min-width="160" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP" width="140" />
        <el-table-column prop="slice" label="切片" width="160" />
        <el-table-column prop="flow_id" label="Flow" min-width="140" show-overflow-tooltip />
        <el-table-column label="P4 详情" min-width="220">
          <template #default="scope">
            <span class="kv">stage: <b>{{ scope.row.p4_stage || '-' }}</b></span>
            <span class="kv">table: <b>{{ scope.row.p4_table || '-' }}</b></span>
            <span class="kv">action: <b>{{ scope.row.p4_action || '-' }}</b></span>
          </template>
        </el-table-column>
        <el-table-column prop="metric" label="指标" width="160">
          <template #default="scope">
            <span v-if="scope.row.metric">{{ scope.row.metric }} = {{ scope.row.metric_value }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="240" show-overflow-tooltip />
      </el-table>
      <div class="footer">
        <span>共 {{ filtered.length }} 条</span>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';

interface TelemetryEvent {
  id: number;
  event_type: string;
  severity: string;
  device_id?: number | null;
  device_name?: string;
  ip_address?: string;
  slice?: string;
  flow_id?: string;
  p4_stage?: string;
  p4_table?: string;
  p4_action?: string;
  metric?: string | null;
  metric_value?: number | null;
  description?: string;
  detected_at: string;
}

const events = ref<TelemetryEvent[]>([]);
const loading = ref(false);
const search = ref('');
const severity = ref<string | null>(null);
const autoRefresh = ref(true);
let timer: number | undefined;

const loadEvents = async () => {
  loading.value = true;
  try {
    const res = await fetch('http://localhost:3001/api/telemetry/events?limit=200');
    const data = await res.json();
    if (Array.isArray(data)) events.value = data;
  } catch (e) {
    // ignore
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadEvents();
  timer = window.setInterval(() => { if (autoRefresh.value) loadEvents(); }, 5000);
});

watch(autoRefresh, v => { if (!v) return; loadEvents(); });

const filtered = computed(() => {
  const key = search.value.trim().toLowerCase();
  return events.value.filter(e => {
    const passKey = !key || [e.device_name, e.ip_address, e.slice, e.event_type, e.description, e.flow_id].some(x => (x || '').toLowerCase().includes(key));
    const passSev = !severity.value || e.severity === severity.value;
    return passKey && passSev;
  });
});

const typeColor = (t: string) => (t === 'gray_failure' ? 'danger' : t === 'packet_loss' ? 'warning' : 'info');
const severityColor = (s: string) => (s === 'critical' ? 'danger' : s === 'major' ? 'warning' : s === 'minor' ? 'info' : '');
</script>

<style scoped>
.telemetry-container { padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.controls { display: flex; gap: 10px; align-items: center; }
.table-card { margin-top: 12px; }
.kv { margin-right: 12px; color: #555; }
.footer { padding: 10px 0; color: #666; }
</style>
