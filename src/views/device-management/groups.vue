<template>
    <div class="groups-management-container">
        <div class="page-header">
            <h2>组管理</h2>
        </div>

        <!-- 添加设备组表单 -->
        <el-card shadow="hover" class="form-card">
            <div class="card-header">
                <h3>添加设备组</h3>
            </div>
            <el-form :model="groupForm" ref="groupFormRef" :rules="groupRules" label-width="100px">
                <el-row :gutter="20">
                    <el-col :span="8">
                        <el-form-item label="组名称" prop="name">
                            <el-input v-model="groupForm.name" placeholder="请输入组名称" />
                        </el-form-item>
                    </el-col>
                    <el-col :span="8">
                        <el-form-item label="设备类型" prop="device_type">
                            <el-select v-model="groupForm.device_type" placeholder="请选择设备类型">
                                <el-option label="Cisco" value="Cisco" />
                                <el-option label="Huawei" value="Huawei" />
                                <el-option label="Juniper" value="Juniper" />
                                <el-option label="H3C" value="H3C" />
                                <el-option label="Ruijie" value="Ruijie" />
                                <el-option label="其他" value="Other" />
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="8">
                        <el-form-item label="身份信息" prop="description">
                            <el-input v-model="groupForm.description" placeholder="请输入身份信息" />
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-form-item>
                    <el-button type="primary" @click="submitForm" :loading="submitting">
                        <el-icon><Plus /></el-icon>
                        添加组
                    </el-button>
                    <el-button @click="resetForm">重置</el-button>
                </el-form-item>
            </el-form>
        </el-card>

        <!-- 设备组列表 -->
        <el-card shadow="hover" class="table-card">
            <div class="card-header">
                <h3>设备组列表</h3>
                <div class="table-controls">
                    <el-input
                        v-model="searchText"
                        placeholder="搜索组名称..."
                        style="width: 200px; margin-right: 10px;"
                        clearable
                    >
                        <template #prefix>
                            <el-icon><Search /></el-icon>
                        </template>
                    </el-input>
                </div>
            </div>
            
            <el-table 
                :data="filteredGroups" 
                style="width: 100%"
                v-loading="loading"
                border
            >
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="name" label="组名称" :min-width="140" show-overflow-tooltip />
                <el-table-column prop="device_type" label="设备类型" width="120">
                    <template #default="scope">
                        <el-tag :type="getDeviceTypeColor(scope.row.device_type)">
                            {{ getDeviceTypeName(scope.row.device_type) }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="description" label="身份信息" :min-width="180" show-overflow-tooltip />
                <el-table-column prop="created_at" label="创建时间" width="180" />
                <el-table-column label="操作" width="190">
                    <template #default="scope">
                        <div class="actions-cell">
                            <el-button 
                                type="warning" 
                                size="small"
                                @click="editGroup(scope.row)"
                            >
                                <el-icon><Edit /></el-icon>
                                编辑
                            </el-button>
                            <el-button 
                                type="danger" 
                                size="small"
                                @click="deleteGroup(scope.row)"
                            >
                                <el-icon><Delete /></el-icon>
                                删除
                            </el-button>
                        </div>
                    </template>
                </el-table-column>
            </el-table>
            
            <div class="pagination-container">
                <div class="pagination-info">
                    <span>显示条数：</span>
                    <el-select v-model="pageSize" @change="handlePageSizeChange" style="width: 80px;">
                        <el-option label="10" :value="10" />
                        <el-option label="20" :value="20" />
                        <el-option label="50" :value="50" />
                        <el-option label="100" :value="100" />
                    </el-select>
                </div>
                <el-pagination
                    v-model:current-page="currentPage"
                    :page-size="pageSize"
                    :total="total"
                    layout="total, prev, pager, next, jumper"
                    @size-change="handlePageSizeChange"
                    @current-change="handleCurrentChange"
                />
            </div>
        </el-card>

        <!-- 编辑组对话框 -->
        <el-dialog v-model="editDialogVisible" title="编辑设备组" width="500px">
            <el-form :model="editForm" :rules="groupRules" label-width="100px">
                <el-form-item label="组名称" prop="name">
                    <el-input v-model="editForm.name" placeholder="请输入组名称" />
                </el-form-item>
                <el-form-item label="设备类型" prop="device_type">
                    <el-select v-model="editForm.device_type" placeholder="请选择设备类型">
                        <el-option label="Cisco" value="Cisco" />
                        <el-option label="Huawei" value="Huawei" />
                        <el-option label="Juniper" value="Juniper" />
                        <el-option label="H3C" value="H3C" />
                        <el-option label="其他" value="Other" />
                    </el-select>
                </el-form-item>
                <el-form-item label="身份信息" prop="description">
                    <el-input v-model="editForm.description" placeholder="请输入身份信息" />
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="editDialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="updateGroup" :loading="updating">确定</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue';

// 表单数据
const groupForm = ref({
    name: '',
    device_type: '',
    description: ''
});

const editForm = ref({
    id: null,
    name: '',
    device_type: '',
    description: ''
});

// 表单验证规则
const groupRules = {
    name: [
        { required: true, message: '请输入组名称', trigger: 'blur' }
    ],
    device_type: [
        { required: true, message: '请选择设备类型', trigger: 'change' }
    ],
    description: [
        { required: true, message: '请输入身份信息', trigger: 'blur' }
    ]
};

// 状态管理
const loading = ref(false);
const submitting = ref(false);
const updating = ref(false);
const editDialogVisible = ref(false);

// 分页和搜索
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const searchText = ref('');

// 设备组列表
const groups = ref([]);

// 计算属性
const filteredGroups = computed(() => {
    let filtered = groups.value;
    if (searchText.value) {
        filtered = filtered.filter(group => 
            group.name.toLowerCase().includes(searchText.value.toLowerCase())
        );
    }
    
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    total.value = filtered.length;
    
    return filtered.slice(start, end);
});

// 方法
const getDeviceTypeName = (type) => {
    const typeMap = {
        'Cisco': 'Cisco',
        'Huawei': 'Huawei',
        'Juniper': 'Juniper',
        'H3C': 'H3C',
        'Ruijie': 'Ruijie',
        'Other': '其他'
    };
    return typeMap[type] || type;
};

const getDeviceTypeColor = (type) => {
    const colorMap = {
        router: 'primary',
        switch: 'success',
        firewall: 'warning',
        server: 'info',
        other: 'default'
    };
    return colorMap[type] || 'default';
};

const submitForm = async () => {
    submitting.value = true;
    try {
        const payload = {
            name: groupForm.value.name,
            device_type: groupForm.value.device_type,
            description: groupForm.value.description
        };
        const res = await fetch('http://localhost:3001/api/device-groups', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || '添加失败');
        ElMessage.success('设备组添加成功');
        resetForm();
        await loadGroups();
    } catch (error) {
        ElMessage.error('添加失败');
    } finally {
        submitting.value = false;
    }
};

const resetForm = () => {
    groupForm.value = {
        name: '',
        device_type: '',
    description: ''
    };
};

const editGroup = (group) => {
    editForm.value = { ...group };
    editDialogVisible.value = true;
};

const updateGroup = async () => {
    updating.value = true;
    try {
        const payload = {
            name: editForm.value.name,
            device_type: editForm.value.device_type,
            description: editForm.value.description
        };
        const res = await fetch(`http://localhost:3001/api/device-groups/${editForm.value.id}` , {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || '更新失败');
        ElMessage.success('更新成功');
        editDialogVisible.value = false;
        await loadGroups();
    } catch (error) {
        ElMessage.error('更新失败');
    } finally {
        updating.value = false;
    }
};

const deleteGroup = async (group) => {
    try {
        await ElMessageBox.confirm(
            `确定要删除设备组 "${group.name}" 吗？`,
            '确认删除',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
            }
        );
    const res = await fetch(`http://localhost:3001/api/device-groups/${group.id}` , { method: 'DELETE' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '删除失败');
    ElMessage.success('删除成功');
    await loadGroups();
    } catch {
        ElMessage.info('取消删除');
    }
};

const handlePageSizeChange = (size) => {
    pageSize.value = size;
    currentPage.value = 1;
};

const handleCurrentChange = (page) => {
    currentPage.value = page;
};

const loadGroups = async () => {
    loading.value = true;
    try {
        const response = await fetch('http://localhost:3001/api/device-groups');
        const data = await response.json();
        
        if (response.ok) {
            groups.value = data.map(group => ({
                ...group,
                deviceType: group.device_type,
                createTime: new Date(group.created_at).toLocaleString()
            }));
            total.value = data.length;
        } else {
            throw new Error(data.error || '加载失败');
        }
    } catch (error) {
        console.error('加载设备组错误:', error);
        ElMessage.error('加载设备组失败');
        
        // 使用备用数据
        groups.value = [
            {
                id: 1,
                name: '核心路由组',
                device_type: 'Cisco',
                description: 'admin:admin123',
                created_at: '2023-08-20 10:30:00'
            },
            {
                id: 2,
                name: '接入交换组',
                device_type: 'Huawei',
                description: 'admin:switch123',
                created_at: '2023-08-20 11:15:00'
            }
        ];
    total.value = groups.value.length;
    } finally {
        loading.value = false;
    }
};

// 生命周期
onMounted(() => {
    loadGroups();
});
</script>

<style scoped>
.groups-management-container {
    padding: 20px;
    background-color: #f5f5f5;
    min-height: 100vh;
}

.page-header {
    margin-bottom: 20px;
}

.page-header h2 {
    margin: 0;
    color: #2c3e50;
}

.form-card, .table-card {
    margin-bottom: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ebeef5;
}

.card-header h3 {
    margin: 0;
    color: #2c3e50;
}

.table-controls {
    display: flex;
    align-items: center;
}

.pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.pagination-info {
    display: flex;
    align-items: center;
    gap: 10px;
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.actions-cell {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
}
</style>
