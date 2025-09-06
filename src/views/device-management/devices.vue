<template>
    <div>
        <div class="container">
            <div class="handle-box">
                <el-button type="primary" @click="handleAdd">添加网络设备</el-button>
                <el-input v-model="query.name" placeholder="搜索" class="handle-input mr10"></el-input>
            </div>
            <el-table :data="pagedTableData" border class="table" ref="multipleTable" header-cell-class-name="table-header">
                <el-table-column prop="id" label="ID" width="55" align="center"></el-table-column>
                <el-table-column prop="name" label="设备名称"></el-table-column>
                <el-table-column prop="ip_address" label="IP地址"></el-table-column>
                <el-table-column prop="group_name" label="设备组"></el-table-column>
                <el-table-column prop="description" label="描述"></el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
                <el-table-column label="操作" width="220" align="center">
                    <template #default="scope">
                        <el-button text :icon="Edit" @click="handleEdit(scope.$index, scope.row)" v-permiss="15" style="color: orange;">
                            编辑
                        </el-button>
                        <el-button text :icon="Delete" class="red" @click="handleDelete(scope.$index, scope.row)" v-permiss="16" style="color: red;">
                            删除
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
            <div class="pagination">
                <el-pagination
                    background
                    layout="total, sizes, prev, pager, next"
                    :current-page="query.pageIndex"
                    :page-size="query.pageSize"
                    :page-sizes="[10, 20, 50, 100]"
                    :total="filteredData.length"
                    @current-change="handlePageChange"
                    @size-change="handleSizeChange"
                ></el-pagination>
            </div>
        </div>

        <!-- 编辑弹出框 -->
        <el-dialog :title="editMode ? '编辑网络设备' : '新增网络设备'" v-model="editVisible" width="520px">
            <el-form label-width="100px" :model="form">
                <el-form-item label="设备名称">
                    <el-input v-model="form.name"></el-input>
                </el-form-item>
                <el-form-item label="IP地址">
                    <el-input v-model="form.ip_address"></el-input>
                </el-form-item>
                <el-form-item label="设备组">
                    <el-select v-model="form.group_id" placeholder="请选择设备组" style="width: 100%;">
                        <el-option v-for="g in groupOptions" :key="g.id" :label="`${g.name} (${g.device_type})`" :value="g.id" />
                    </el-select>
                </el-form-item>
                <el-form-item label="描述信息">
                    <el-input v-model="form.description"></el-input>
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="editVisible = false">取 消</el-button>
                    <el-button type="primary" @click="saveEdit">确 定</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts" name="device-devices">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Delete, Edit } from '@element-plus/icons-vue';

interface DeviceItem {
    id: number;
    name: string;
    ip_address: string;
    group_id: number;
    group_name: string;
    device_type?: string;
    description?: string;
    created_at?: string;
}

const query = reactive({
    name: '',
    pageIndex: 1,
    pageSize: 10,
});
const tableData = ref<DeviceItem[]>([]);
const groupOptions = ref<any[]>([]);

const loadGroups = async () => {
    try {
        const res = await fetch('http://localhost:3001/api/device-groups');
        const data = await res.json();
        if (Array.isArray(data)) groupOptions.value = data;
    } catch (e) {
        groupOptions.value = [];
    }
};

const loadDevices = async () => {
    try {
        const res = await fetch('http://localhost:3001/api/devices');
        const data = await res.json();
        if (Array.isArray(data)) tableData.value = data as DeviceItem[];
    } catch (e) {
        ElMessage.error('加载设备失败');
    }
};

const filteredData = computed(() => {
    return tableData.value.filter(item => {
        const key = query.name.toLowerCase();
        return (
            item.name.toLowerCase().includes(key) ||
            (item.ip_address || '').toLowerCase().includes(key) ||
            (item.group_name || '').toLowerCase().includes(key)
        );
    });
});

const pagedTableData = computed(() => {
    const start = (query.pageIndex - 1) * query.pageSize;
    const end = start + query.pageSize;
    return filteredData.value.slice(start, end);
});

// 分页导航
const handlePageChange = (val: number) => {
    query.pageIndex = val;
};
const handleSizeChange = (val: number) => {
    query.pageSize = val;
}

// 删除操作
const handleDelete = async (index: number, row: any) => {
    try {
        await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' });
        const res = await fetch(`http://localhost:3001/api/devices/${row.id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('删除失败');
        ElMessage.success('删除成功');
        await loadDevices();
    } catch (e) {
        // 用户取消或失败
    }
};

// 表格编辑时弹窗和保存
const editVisible = ref(false);
const editMode = ref(false);
let form = reactive<any>({
    id: -1,
    name: '',
    ip_address: '',
    group_id: null,
    description: ''
});
const handleAdd = () => {
    editMode.value = false;
    form.id = -1;
    form.name = '';
    form.ip_address = '';
    form.group_id = null;
    form.description = '';
    editVisible.value = true;
}
const handleEdit = (index: number, row: any) => {
    editMode.value = true;
    Object.assign(form, {
        id: row.id,
        name: row.name,
        ip_address: row.ip_address,
        group_id: row.group_id,
        description: row.description || ''
    });
    editVisible.value = true;
};
const saveEdit = async () => {
    try {
        const payload = { name: form.name, ip_address: form.ip_address, group_id: form.group_id, description: form.description };
        let res: Response;
        if (editMode.value) {
            res = await fetch(`http://localhost:3001/api/devices/${form.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        } else {
            res = await fetch('http://localhost:3001/api/devices', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        }
        if (!res.ok) throw new Error('保存失败');
        ElMessage.success(editMode.value ? '修改成功' : '添加成功');
        editVisible.value = false;
        await loadDevices();
    } catch (e:any) {
        ElMessage.error(e.message || '保存失败');
    }
};

onMounted(() => {
    loadGroups();
    loadDevices();
});

</script>

<style scoped>
.handle-box {
    margin-bottom: 20px;
}
.handle-input {
    width: 300px;
}
.table {
    width: 100%;
    font-size: 14px;
}
.red {
    color: #F56C6C;
}
.mr10 {
    margin-right: 10px;
}
</style>
