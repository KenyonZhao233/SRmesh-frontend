<template>
  <div class="collector-container">
    <div class="page-header">
      <h2>遥测收集器管理</h2>
      <div class="controls">
        <el-input v-model="search" placeholder="搜索名称/地址..." clearable style="width: 240px" />
        <el-button type="primary" @click="openCreate">新增收集器</el-button>
        <el-button @click="loadCollectors" :loading="loading">刷新</el-button>
      </div>
    </div>

    <el-card shadow="hover" class="table-card">
      <el-table :data="filtered" border v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="protocol" label="协议" width="100" />
        <el-table-column prop="address" label="地址" width="160" />
        <el-table-column prop="port" label="端口" width="90" />
        <el-table-column prop="enabled" label="启用" width="90">
          <template #default="scope">
            <el-tag :type="scope.row.enabled ? 'success' : 'info'">{{ scope.row.enabled ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'online' ? 'success' : (scope.row.status === 'offline' ? 'danger' : 'info')">
              {{ scope.row.status || 'unknown' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_heartbeat" label="上次心跳" width="180" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="260">
          <template #default="scope">
            <el-button size="small" @click="testHealth(scope.row)">健康检查</el-button>
            <el-button size="small" type="warning" @click="openEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="editing ? '编辑收集器' : '新增收集器'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型"><el-select v-model="form.type"><el-option label="server" value="server" /></el-select></el-form-item>
        <el-form-item label="协议"><el-select v-model="form.protocol"><el-option label="gNMI" value="gNMI" /><el-option label="INT" value="INT" /><el-option label="SNMP" value="SNMP" /></el-select></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="端口"><el-input v-model.number="form.port" type="number" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDialog = false">取消</el-button>
          <el-button type="primary" @click="save">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

interface Collector {
  id?: number;
  name: string;
  type: string;
  protocol: string;
  address: string;
  port?: number | null;
  enabled: boolean | number;
  status?: string;
  last_heartbeat?: string | null;
  description?: string | null;
}

const loading = ref(false);
const list = ref<Collector[]>([]);
const search = ref('');
const showDialog = ref(false);
const editing = ref(false);
const form = ref<Collector>({ name: '', type: 'server', protocol: 'gNMI', address: '', port: null, enabled: true, description: '' });

const loadCollectors = async () => {
  loading.value = true;
  try {
    const res = await fetch('http://localhost:3001/api/telemetry/collectors');
    const data = await res.json();
    list.value = data.map((d: any) => ({ ...d, enabled: !!d.enabled }));
  } catch (e) {
    list.value = [];
  } finally {
    loading.value = false;
  }
};

const filtered = computed(() => {
  const key = search.value.toLowerCase();
  return list.value.filter(c => !key || [c.name, c.address, c.protocol, c.status].some(v => (v || '').toLowerCase().includes(key)));
});

const openCreate = () => {
  editing.value = false;
  form.value = { name: '', type: 'server', protocol: 'gNMI', address: '', port: null, enabled: true, description: '' };
  showDialog.value = true;
};

const openEdit = (row: Collector) => {
  editing.value = true;
  form.value = { ...row };
  showDialog.value = true;
};

const save = async () => {
  try {
    const payload = { ...form.value, enabled: form.value.enabled ? 1 : 0 };
    if (editing.value && form.value.id) {
      const res = await fetch(`http://localhost:3001/api/telemetry/collectors/${form.value.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!res.ok) throw new Error('更新失败');
      ElMessage.success('更新成功');
    } else {
      const res = await fetch('http://localhost:3001/api/telemetry/collectors', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!res.ok) throw new Error('创建失败');
      ElMessage.success('创建成功');
    }
    showDialog.value = false;
    loadCollectors();
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败');
  }
};

const remove = async (row: Collector) => {
  try {
    await ElMessageBox.confirm(`确认删除 ${row.name} ?`, '提示', { type: 'warning' });
    const res = await fetch(`http://localhost:3001/api/telemetry/collectors/${row.id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('删除失败');
    ElMessage.success('删除成功');
    loadCollectors();
  } catch {}
};

const testHealth = async (row: Collector) => {
  try {
    const res = await fetch(`http://localhost:3001/api/telemetry/collectors/${row.id}/health`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error('检查失败');
    ElMessage.success(`状态: ${data.status}`);
    loadCollectors();
  } catch (e: any) {
    ElMessage.error(e.message || '检查失败');
  }
};

onMounted(() => { loadCollectors(); });
</script>

<style scoped>
.collector-container { padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.controls { display: flex; gap: 10px; align-items: center; }
.table-card { margin-top: 12px; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px; }
</style>
