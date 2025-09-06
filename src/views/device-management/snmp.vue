<template>
  <div class="snmp-container">
    <div class="page-header">
      <h2>SNMP 信息</h2>
      <div class="controls">
        <el-select v-model="selectedId" placeholder="选择设备" filterable style="min-width: 280px" @change="fetchSnmp">
          <el-option v-for="d in devices" :key="d.id" :label="`${d.name} (${d.ip_address})`" :value="d.id" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="fetchSnmp">刷新</el-button>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>设备基本信息</template>
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="名称">{{ snmp?.device?.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="IP">{{ snmp?.device?.ip_address || '-' }}</el-descriptions-item>
            <el-descriptions-item label="设备组">{{ snmp?.device?.group_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ snmp?.device?.device_type || '-' }}</el-descriptions-item>
            <el-descriptions-item label="sysName">{{ snmp?.sys?.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="sysDescr">{{ snmp?.sys?.descr || '-' }}</el-descriptions-item>
            <el-descriptions-item label="sysObjectID">{{ snmp?.sys?.objectId || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Uptime">{{ formatUptime(snmp?.sys?.upTimeSeconds) }}</el-descriptions-item>
            <el-descriptions-item label="轮询时间">{{ formatTime(snmp?.polledAt) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>资源使用</template>
          <div class="metrics">
            <div class="metric">
              <div class="metric-label">CPU</div>
              <el-progress :percentage="snmp?.resources?.cpuPercent || 0" :stroke-width="14" status="success" />
            </div>
            <div class="metric">
              <div class="metric-label">内存 {{ snmp?.resources?.memory?.usedMB || 0 }} / {{ snmp?.resources?.memory?.totalMB || 0 }} MB</div>
              <el-progress :percentage="snmp?.resources ? snmp.resources.memory?.percent || 0 : 0" :stroke-width="14" />
            </div>
            <div class="metric">
              <div class="metric-label">接口状态 Up/Down</div>
              <el-tag type="success" class="mr8">Up {{ snmp?.stats?.upCount || 0 }}</el-tag>
              <el-tag type="danger">Down {{ snmp?.stats?.downCount || 0 }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>快速操作</template>
          <div class="quick-actions">
            <el-button @click="copyText(snmp?.sys?.descr || '')">复制 sysDescr</el-button>
            <el-button @click="copyText(snmp?.device?.ip_address || '')">复制 IP</el-button>
          </div>
          <div v-if="error" class="error">{{ error }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="table-card">
      <template #header>接口列表</template>
      <el-table :data="snmp?.interfaces || []" v-loading="loading" border style="width: 100%">
        <el-table-column prop="index" label="#" width="60" />
        <el-table-column prop="name" label="接口" min-width="140" />
        <el-table-column prop="speedMbps" label="速率(Mbps)" width="120" />
        <el-table-column label="状态" width="160">
          <template #default="scope">
            <el-tag size="small" type="success" v-if="scope.row.adminStatus === 'up'">admin up</el-tag>
            <el-tag size="small" type="info" v-else>admin down</el-tag>
            <el-tag size="small" :type="scope.row.operStatus === 'up' ? 'success' : 'danger'" style="margin-left:6px;">
              oper {{ scope.row.operStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inOctets" label="In Octets" width="140" />
        <el-table-column prop="outOctets" label="Out Octets" width="140" />
        <el-table-column prop="inErrors" label="In Err" width="100" />
        <el-table-column prop="outErrors" label="Out Err" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

interface Device { id: number; name: string; ip_address: string; group_name?: string; device_type?: string }
interface SnmpPayload {
  device: Device;
  sys: { name: string; descr: string; objectId: string; upTimeSeconds: number };
  resources: { cpuPercent: number; memory: { usedMB: number; totalMB: number; percent: number } };
  interfaces: Array<{ index: number; name: string; adminStatus: string; operStatus: string; speedMbps: number; inOctets: number; outOctets: number; inErrors: number; outErrors: number }>;
  stats: { upCount: number; downCount: number };
  polledAt: string;
}

const devices = ref<Device[]>([]);
const selectedId = ref<number | null>(null);
const snmp = ref<SnmpPayload | null>(null);
const loading = ref(false);
const error = ref('');

const loadDevices = async () => {
  try {
    const res = await fetch('http://localhost:3001/api/devices');
    const data = await res.json();
    if (Array.isArray(data)) {
      devices.value = data;
      if (!selectedId.value && data.length) {
        selectedId.value = data[0].id;
        fetchSnmp();
      }
    }
  } catch (e) {
    devices.value = [];
  }
};

const fetchSnmp = async () => {
  if (!selectedId.value) return;
  loading.value = true;
  error.value = '';
  try {
    const res = await fetch(`http://localhost:3001/api/snmp/${selectedId.value}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '加载失败');
    snmp.value = data as SnmpPayload;
  } catch (e: any) {
    error.value = e.message || '获取失败';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
};

const copyText = async (text: string) => {
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success('已复制到剪贴板');
  } catch (e) {
    ElMessage.error('复制失败');
  }
};

const formatTime = (iso?: string) => {
  if (!iso) return '-';
  const d = new Date(iso);
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
};

const formatUptime = (sec?: number) => {
  if (!sec) return '-';
  const d = Math.floor(sec / 86400);
  const h = Math.floor((sec % 86400) / 3600);
  const m = Math.floor((sec % 3600) / 60);
  return `${d}天 ${h}小时 ${m}分钟`;
};

onMounted(() => {
  loadDevices();
});
</script>

<style scoped>
.snmp-container { padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.page-header h2 { margin: 0; }
.controls { display: flex; gap: 10px; align-items: center; }
.info-card { margin-bottom: 16px; }
.table-card { margin-top: 16px; }
.metrics { display: flex; flex-direction: column; gap: 12px; }
.metric-label { margin-bottom: 6px; color: #555; }
.mr8 { margin-right: 8px; }
.error { margin-top: 8px; color: #c0392b; }
</style>
