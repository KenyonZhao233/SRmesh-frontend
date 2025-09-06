<template>
    <div class="task-management-container">
        <div class="page-header">
            <h2>任务管理</h2>
        </div>

        <!-- 创建任务 -->
        <el-card shadow="hover" class="task-form-card">
            <div class="card-header">
                <h3>创建新任务</h3>
            </div>
            
            <el-form :model="taskForm" ref="taskFormRef" :rules="taskRules" label-width="120px">
                <el-row :gutter="20">
                    <el-col :span="12">
                        <el-form-item label="任务名称" prop="name">
                            <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="任务类型" prop="type">
                            <el-select v-model="taskForm.type" placeholder="请选择任务类型" style="width: 100%;">
                                <el-option label="配置更新" value="config" />
                                <el-option label="状态检查" value="status" />
                                <el-option label="性能监控" value="monitor" />
                                <el-option label="自定义命令" value="custom" />
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-row :gutter="20">
                    <el-col :span="24">
                        <el-form-item label="目标设备" prop="targetDevices">
                            <el-input 
                                v-model="taskForm.targetDevices"
                                type="textarea" 
                                :rows="6"
                                placeholder="每行一个目标，支持以下格式：&#10;host:设备名称或IP地址&#10;group:设备组名称&#10;&#10;示例：&#10;host:192.168.1.1&#10;host:RTR-CORE-01&#10;group:核心路由组"
                                style="width: 100%;"
                                @input="validateTargets"
                            />
                            <div class="input-hint">
                                <el-icon><InfoFilled /></el-icon>
                                每行一个目标，支持输入host:设备名称或者IP地址，group:设备组名称，所有设备必须是相同类型
                            </div>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-row :gutter="20">
                    <el-col :span="12">
                        <el-form-item label="执行策略" prop="strategy">
                            <el-select v-model="taskForm.strategy" placeholder="请选择执行策略" style="width: 100%;">
                                <el-option label="并行执行" value="parallel" />
                                <el-option label="串行执行" value="serial" />
                                <el-option label="分批执行" value="batch" />
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="设备类型" v-if="resolvedDevices.length > 0">
                            <el-tag 
                                :type="deviceTypeValid ? 'success' : 'danger'"
                                size="large"
                            >
                                {{ deviceTypeValid ? `${getDeviceTypeName(commonDeviceType)} (类型一致)` : '设备类型不一致' }}
                            </el-tag>
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-form-item label="CLI命令" prop="command">
                    <el-input 
                        v-model="taskForm.command"
                        type="textarea" 
                        :rows="8"
                        placeholder="请输入CLI命令，支持多行命令&#10;&#10;示例：&#10;show version&#10;show ip interface brief&#10;show running-config"
                        style="width: 100%;"
                    />
                    <div class="input-hint">
                        <el-icon><InfoFilled /></el-icon>
                        支持多行命令，系统将按顺序执行每一行命令
                    </div>
                </el-form-item>

                <!-- 目标预览 -->
                <el-form-item label="目标预览" v-if="taskForm.targetDevices && resolvedDevices.length > 0">
                    <div class="target-preview">
                        <div class="preview-header">
                            <span>目标列表：</span>
                            <el-button size="small" @click="validateTargets" type="primary">重新验证</el-button>
                        </div>
                        
                        <!-- 解析的目标列表 -->
                        <div class="target-list">
                            <h4>解析的目标：</h4>
                            <div class="target-items">
                                <el-tag 
                                    v-for="(target, index) in parsedTargets" 
                                    :key="index"
                                    :type="target.valid ? 'success' : 'danger'"
                                    class="target-tag"
                                >
                                    {{ target.type }}:{{ target.value }}
                                    <span v-if="!target.valid"> (无效)</span>
                                </el-tag>
                            </div>
                        </div>
                        
                        <!-- 实际执行设备 -->
                        <div class="device-count">
                            <h4>实际执行设备：{{ resolvedDevices.length }} 个</h4>
                            <div v-if="!deviceTypeValid" class="type-warning">
                                <el-alert
                                    title="警告：设备类型不一致"
                                    type="warning"
                                    description="任务执行需要所有设备为相同类型"
                                    show-icon
                                    :closable="false"
                                />
                            </div>
                        </div>
                    </div>
                </el-form-item>

                <!-- 命令预览 -->
                <el-form-item label="执行预览" v-if="taskForm.command && resolvedDevices.length > 0">
                    <div class="command-preview">
                        <div class="preview-header">
                            <span>将在 {{ resolvedDevices.length }} 台设备上执行以下命令：</span>
                            <el-button size="small" @click="testCommand">测试命令</el-button>
                        </div>
                        <div class="command-content">
                            <pre>{{ taskForm.command }}</pre>
                        </div>
                        <div class="device-list">
                            <h4>目标设备列表：</h4>
                            <el-table :data="resolvedDevices" border size="small" max-height="200">
                                <el-table-column prop="name" label="设备名称" />
                                <el-table-column prop="ip_address" label="IP地址" />
                                <el-table-column prop="group_name" label="设备组" />
                            </el-table>
                        </div>
                    </div>
                </el-form-item>

                <el-form-item>
                    <el-button 
                        type="primary" 
                        @click="createTask" 
                        :loading="creating"
                        :disabled="!resolvedDevices.length || !deviceTypeValid"
                    >
                        <el-icon><Plus /></el-icon>
                        创建并执行任务
                    </el-button>
                    <el-button @click="resetTaskForm">重置</el-button>
                </el-form-item>
            </el-form>
        </el-card>

        <!-- 任务列表 -->
        <el-card shadow="hover" class="task-list-card">
            <div class="card-header">
                <h3>任务列表</h3>
                <div class="task-controls">
                    <el-select v-model="filterStatus" placeholder="筛选状态" style="width: 150px; margin-right: 10px;">
                        <el-option label="全部" value="" />
                        <el-option label="运行中" value="running" />
                        <el-option label="已完成" value="completed" />
                        <el-option label="失败" value="failed" />
                        <el-option label="等待中" value="pending" />
                    </el-select>
                    <el-button @click="refreshTasks">
                        <el-icon><Refresh /></el-icon>
                        刷新
                    </el-button>
                </div>
            </div>
            
            <el-table :data="filteredTasks" border v-loading="loading">
                <el-table-column prop="id" label="任务ID" width="80" />
                <el-table-column prop="name" label="任务名称" />
                <el-table-column prop="type" label="类型" width="100">
                    <template #default="scope">
                        <el-tag>{{ getTaskTypeName(scope.row.type) }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="device_count" label="设备数量" width="100" />
                <el-table-column prop="progress" label="进度" width="120">
                    <template #default="scope">
                        <el-progress 
                            :percentage="scope.row.progress" 
                            :status="getProgressStatus(scope.row.status)"
                            :show-text="false"
                        />
                        <span style="margin-left: 10px;">{{ scope.row.progress }}%</span>
                    </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="180" />
                <el-table-column label="操作" width="150">
                    <template #default="scope">
                        <el-button size="small" @click="viewTaskDetail(scope.row)">详情</el-button>
                        <el-button 
                            size="small" 
                            type="danger" 
                            @click="deleteTask(scope.row.id)"
                        >
                            删除
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="totalTasks"
                layout="total, sizes, prev, pager, next, jumper"
                style="margin-top: 20px; justify-content: center;"
                @size-change="loadTasks"
                @current-change="loadTasks"
            />
        </el-card>

        <!-- 任务详情对话框 -->
        <el-dialog v-model="detailDialogVisible" title="任务详情" width="80%" :before-close="closeDetailDialog">
            <div v-if="currentTask">
                <el-descriptions :column="2" border>
                    <el-descriptions-item label="任务ID">{{ currentTask.id }}</el-descriptions-item>
                    <el-descriptions-item label="任务名称">{{ currentTask.name }}</el-descriptions-item>
                    <el-descriptions-item label="任务类型">{{ getTaskTypeName(currentTask.type) }}</el-descriptions-item>
                    <el-descriptions-item label="执行策略">{{ getStrategyName(currentTask.strategy) }}</el-descriptions-item>
                    <el-descriptions-item label="设备数量">{{ currentTask.device_count }}</el-descriptions-item>
                    <el-descriptions-item label="任务状态">
                        <el-tag :type="getStatusType(currentTask.status)">
                            {{ getStatusName(currentTask.status) }}
                        </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="创建时间">{{ currentTask.created_at }}</el-descriptions-item>
                    <el-descriptions-item label="完成时间">{{ currentTask.finished_at || '未完成' }}</el-descriptions-item>
                </el-descriptions>

                <h4 style="margin: 20px 0 10px 0;">执行命令：</h4>
                <pre class="command-display">{{ currentTask.command }}</pre>

                <h4 style="margin: 20px 0 10px 0;">设备执行结果：</h4>
                <el-table :data="currentTask.deviceResults" border>
                    <el-table-column prop="device_name" label="设备名称" />
                    <el-table-column prop="ip_address" label="IP地址" />
                    <el-table-column prop="output" label="输出结果" show-overflow-tooltip />
                    <el-table-column prop="error" label="错误信息" show-overflow-tooltip />
                </el-table>
            </div>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, InfoFilled, Refresh } from '@element-plus/icons-vue';

// 表单数据
const taskForm = ref({
    name: '',
    type: '',
    targetDevices: '',
    strategy: 'parallel',
    command: ''
});

// 表单验证规则
const taskRules = {
    name: [
        { required: true, message: '请输入任务名称', trigger: 'blur' }
    ],
    type: [
        { required: true, message: '请选择任务类型', trigger: 'change' }
    ],
    targetDevices: [
        { required: true, message: '请输入目标设备', trigger: 'blur' }
    ],
    strategy: [
        { required: true, message: '请选择执行策略', trigger: 'change' }
    ],
    command: [
        { required: true, message: '请输入CLI命令', trigger: 'blur' }
    ]
};

// 状态管理
const loading = ref(false);
const creating = ref(false);

// 分页和筛选
const currentPage = ref(1);
const pageSize = ref(10);
const totalTasks = ref(0);
const filterStatus = ref('');
const detailDialogVisible = ref(false);
const currentTask = ref(null);

// 数据列表
const tasks = ref([]);
const deviceGroups = ref([]);
const allDevices = ref([]);

// 计算属性
const parsedTargets = computed(() => {
    if (!taskForm.value.targetDevices) return [];
    
    return taskForm.value.targetDevices
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => {
            const [type, value] = line.split(':');
            if (!type || !value) {
                return {
                    type: type || '',
                    value: value || line,
                    valid: false,
                    error: '格式错误，应为 type:value'
                };
            }
            
            const trimmedType = type.trim().toLowerCase();
            const trimmedValue = value.trim();
            
            if (!['host', 'group'].includes(trimmedType)) {
                return {
                    type: trimmedType,
                    value: trimmedValue,
                    valid: false,
                    error: '类型必须是 host 或 group'
                };
            }
            
            return {
                type: trimmedType,
                value: trimmedValue,
                valid: true,
                error: ''
            };
        });
});

const resolvedDevices = computed(() => {
    const devices = [];
    const validTargets = parsedTargets.value.filter(t => t.valid);
    
    validTargets.forEach(target => {
        if (target.type === 'host') {
            // 查找设备（按名称或IP地址）
            const device = allDevices.value.find(d => 
                d.name === target.value || d.ip_address === target.value
            );
            if (device && !devices.find(d => d.id === device.id)) {
                devices.push(device);
            }
        } else if (target.type === 'group') {
            // 查找设备组中的所有设备
            const group = deviceGroups.value.find(g => g.name === target.value);
            if (group) {
                const groupDevices = allDevices.value.filter(d => d.group_id === group.id);
                groupDevices.forEach(device => {
                    if (!devices.find(d => d.id === device.id)) {
                        devices.push(device);
                    }
                });
            }
        }
    });
    
    return devices;
});

// 设备类型验证
const commonDeviceType = computed(() => {
    if (resolvedDevices.value.length === 0) return '';
    const types = [...new Set(resolvedDevices.value.map(d => d.device_type))];
    return types.length === 1 ? types[0] : '';
});

const deviceTypeValid = computed(() => {
    return resolvedDevices.value.length > 0 && commonDeviceType.value !== '';
});

const filteredTasks = computed(() => {
    if (!filterStatus.value) return tasks.value;
    return tasks.value.filter(task => task.status === filterStatus.value);
});

// 方法
const validateTargets = () => {
    if (!taskForm.value.targetDevices) {
        ElMessage.warning('请输入目标设备');
        return;
    }
    
    const invalidTargets = parsedTargets.value.filter(t => !t.valid);
    if (invalidTargets.length > 0) {
        ElMessage.warning(`发现 ${invalidTargets.length} 个无效目标，请检查格式`);
        return;
    }
    
    if (resolvedDevices.value.length === 0) {
        ElMessage.warning('没有找到匹配的设备');
        return;
    }
    
    if (!deviceTypeValid.value) {
        ElMessage.warning('目标设备类型不一致，请选择相同类型的设备');
        return;
    }
    
    ElMessage.success(`目标验证成功，共找到 ${resolvedDevices.value.length} 台设备`);
};

const testCommand = () => {
    if (!taskForm.value.command) {
        ElMessage.warning('请输入CLI命令');
        return;
    }
    
    ElMessage.info('命令测试功能开发中...');
};

const getDeviceTypeName = (type) => {
    const typeMap = {
        'Cisco': 'Cisco设备',
        'Huawei': '华为设备',
        'Juniper': 'Juniper设备',
        'H3C': 'H3C设备',
        'Ruijie': '锐捷设备',
        'Other': '其他设备'
    };
    return typeMap[type] || type;
};

const getTaskTypeName = (type) => {
    const typeMap = {
        config: '配置更新',
        status: '状态检查', 
        monitor: '性能监控',
        custom: '自定义命令'
    };
    return typeMap[type] || type;
};

const getStrategyName = (strategy) => {
    const strategyMap = {
        parallel: '并行执行',
        serial: '串行执行',
        batch: '分批执行'
    };
    return strategyMap[strategy] || strategy;
};

const getStatusName = (status) => {
    const statusMap = {
        pending: '等待中',
        running: '运行中',
        completed: '已完成',
        failed: '失败'
    };
    return statusMap[status] || status;
};

const getStatusType = (status) => {
    const typeMap = {
        pending: 'info',
        running: 'warning',
        completed: 'success',
        failed: 'danger'
    };
    return typeMap[status] || 'info';
};

const getProgressStatus = (status) => {
    if (status === 'completed') return 'success';
    if (status === 'failed') return 'exception';
    return undefined;
};

const createTask = async () => {
    if (!resolvedDevices.value.length) {
        ElMessage.warning('没有选择目标设备');
        return;
    }
    
    if (!deviceTypeValid.value) {
        ElMessage.warning('设备类型不一致，无法创建任务');
        return;
    }
    
    creating.value = true;
    
    try {
        // 创建任务
        const response = await fetch('http://localhost:3001/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: taskForm.value.name,
                type: taskForm.value.type,
                strategy: taskForm.value.strategy,
                command: taskForm.value.command,
                device_ids: resolvedDevices.value.map(d => d.id)
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            ElMessage.success('任务创建成功');
            resetTaskForm();
            loadTasks(); // 重新加载任务列表
        } else {
            throw new Error(result.error || '创建任务失败');
        }
        
    } catch (error) {
        console.error('创建任务错误:', error);
        ElMessage.error(error.message || '创建任务失败');
    } finally {
        creating.value = false;
    }
};

const resetTaskForm = () => {
    taskForm.value = {
        name: '',
        type: '',
        targetDevices: '',
        strategy: 'parallel',
        command: ''
    };
};

const viewTaskDetail = async (task) => {
    try {
        const response = await fetch(`http://localhost:3001/api/tasks/${task.id}`);
        const data = await response.json();
        
        if (response.ok) {
            currentTask.value = data;
            detailDialogVisible.value = true;
        } else {
            throw new Error(data.error || '获取任务详情失败');
        }
    } catch (error) {
        console.error('获取任务详情错误:', error);
        ElMessage.error(error.message || '获取任务详情失败');
    }
};

const closeDetailDialog = () => {
    detailDialogVisible.value = false;
    currentTask.value = null;
};

const deleteTask = async (taskId) => {
    try {
        await ElMessageBox.confirm('确定要删除这个任务吗？', '确认删除', {
            type: 'warning'
        });
        
        const index = tasks.value.findIndex(t => t.id === taskId);
        if (index !== -1) {
            tasks.value.splice(index, 1);
            totalTasks.value--;
            ElMessage.success('任务删除成功');
        }
    } catch {
        // 用户取消删除
    }
};

const refreshTasks = () => {
    loadTasks();
};

const loadDeviceGroups = async () => {
    try {
        const response = await fetch('http://localhost:3001/api/device-groups');
        const data = await response.json();
        
        if (response.ok) {
            deviceGroups.value = data;
        } else {
            throw new Error(data.error || '加载失败');
        }
    } catch (error) {
        console.error('加载设备组错误:', error);
        ElMessage.error('加载设备组失败');
    }
};

const loadAllDevices = async () => {
    try {
        const response = await fetch('http://localhost:3001/api/devices');
        const data = await response.json();
        
        if (response.ok) {
            allDevices.value = data;
        } else {
            throw new Error(data.error || '加载失败');
        }
    } catch (error) {
        console.error('加载设备错误:', error);
        ElMessage.error('加载设备失败');
    }
};

const loadTasks = async () => {
    loading.value = true;
    
    try {
        const response = await fetch('http://localhost:3001/api/tasks');
        const data = await response.json();
        
        if (response.ok) {
            tasks.value = data;
            totalTasks.value = data.length;
        } else {
            throw new Error(data.error || '加载失败');
        }
    } catch (error) {
        console.error('加载任务错误:', error);
        ElMessage.error('加载任务列表失败');
    } finally {
        loading.value = false;
    }
};

// 生命周期
onMounted(() => {
    loadDeviceGroups();
    loadAllDevices();
    loadTasks();
});
</script>

<style scoped>
.task-management-container {
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

.task-form-card, .task-list-card {
    margin-bottom: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.card-header h3 {
    margin: 0;
    color: #2c3e50;
}

.task-controls {
    display: flex;
    align-items: center;
}

.input-hint {
    display: flex;
    align-items: center;
    margin-top: 5px;
    font-size: 12px;
    color: #666;
}

.input-hint .el-icon {
    margin-right: 5px;
}

.target-preview, .command-preview {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 15px;
    background-color: #fafafa;
}

.preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    font-weight: bold;
    color: #2c3e50;
}

.target-items {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 15px;
}

.target-tag {
    margin: 2px;
}

.type-warning {
    margin-top: 10px;
}

.command-content {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 15px;
    font-family: 'Courier New', monospace;
}

.command-content pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.device-list h4 {
    margin: 0 0 10px 0;
    color: #2c3e50;
}

.command-display {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 15px;
    margin: 10px 0;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
}
</style>
