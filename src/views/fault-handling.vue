<template>
    <div class="fault-handling-container">
        <!-- 顶部统计 -->
        <div class="stats-section">
            <el-row :gutter="20">
                <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                    <el-card shadow="hover" class="stats-card">
                        <div class="stats-content">
                            <div class="stats-icon delay">
                                <el-icon size="24"><TrendCharts /></el-icon>
                            </div>
                            <div class="stats-text">
                                <div class="stats-number">{{ stats.delayUp }}</div>
                                <div class="stats-label">延迟上升</div>
                            </div>
                        </div>
                    </el-card>
                </el-col>
                <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                    <el-card shadow="hover" class="stats-card">
                        <div class="stats-content">
                            <div class="stats-icon interrupt">
                                <el-icon size="24"><Warning /></el-icon>
                            </div>
                            <div class="stats-text">
                                <div class="stats-number">{{ stats.interrupt }}</div>
                                <div class="stats-label">中断</div>
                            </div>
                        </div>
                    </el-card>
                </el-col>
                <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                    <el-card shadow="hover" class="stats-card">
                        <div class="stats-content">
                            <div class="stats-icon other">
                                <el-icon size="24"><InfoFilled /></el-icon>
                            </div>
                            <div class="stats-text">
                                <div class="stats-number">{{ stats.other }}</div>
                                <div class="stats-label">其他</div>
                            </div>
                        </div>
                    </el-card>
                </el-col>
                <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                    <el-card shadow="hover" class="stats-card">
                        <div class="stats-content">
                            <div class="stats-icon total">
                                <el-icon size="24"><Operation /></el-icon>
                            </div>
                            <div class="stats-text">
                                <div class="stats-number">{{ stats.total }}</div>
                                <div class="stats-label">总数</div>
                            </div>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <!-- 故障告警表格 -->
        <div class="table-section">
            <el-card shadow="hover" class="table-card">
                <div class="card-header">
                    <h3 class="card-title">故障告警列表</h3>
                    <div class="header-controls">
                        <!-- 筛选控件 -->
                        <el-select v-model="filterStatus" placeholder="按状态筛选" clearable style="width: 120px; margin-right: 10px;">
                            <el-option label="待处理" value="待处理" />
                            <el-option label="处理中" value="处理中" />
                            <el-option label="已解决" value="已解决" />
                        </el-select>
                        <el-select v-model="filterSeverity" placeholder="按级别筛选" clearable style="width: 120px; margin-right: 10px;">
                            <el-option label="高" value="高" />
                            <el-option label="中" value="中" />
                            <el-option label="低" value="低" />
                        </el-select>
                        <el-button @click="clearFilters" style="margin-right: 10px;">
                            清空筛选
                        </el-button>
                        <el-button type="primary" @click="refreshData">
                            <el-icon><Refresh /></el-icon>
                            刷新
                        </el-button>
                    </div>
                </div>

                <el-table 
                    :data="filteredAlerts" 
                    stripe
                    style="width: 100%"
                    v-loading="loading"
                >
                    <el-table-column prop="id" label="告警ID" width="100" />
                    <el-table-column prop="type" label="告警类型" width="120" />
                    <el-table-column prop="description" label="描述" min-width="200" />
                    <el-table-column prop="location" label="位置" width="150" />
                    <el-table-column prop="slice" label="切片" width="120" />
                    <el-table-column prop="createTime" label="发生时间" width="160" />
                    <el-table-column prop="status" label="状态" width="100">
                        <template #default="scope">
                            <el-tag 
                                :type="getStatusTagType(scope.row.status)"
                                size="small"
                            >
                                {{ scope.row.status }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="200" fixed="right">
                        <template #default="scope">
                            <el-button-group size="small">
                                <el-button 
                                    type="primary" 
                                    @click="updateStatus(scope.row, '处理中')"
                                    :disabled="scope.row.status === '处理中' || scope.row.status === '已解决'"
                                >
                                    处理
                                </el-button>
                                <el-button 
                                    type="success" 
                                    @click="updateStatus(scope.row, '已解决')"
                                    :disabled="scope.row.status === '已解决'"
                                >
                                    解决
                                </el-button>
                                <el-button 
                                    type="info" 
                                    @click="viewDetail(scope.row)"
                                >
                                    详情
                                </el-button>
                            </el-button-group>
                        </template>
                    </el-table-column>
                </el-table>

                <!-- 分页 -->
                <div class="pagination-container">
                    <el-pagination
                        v-model:current-page="currentPage"
                        v-model:page-size="pageSize"
                        :page-sizes="[10, 20, 50, 100]"
                        :total="totalCount"
                        layout="total, sizes, prev, pager, next, jumper"
                        @size-change="handleSizeChange"
                        @current-change="handleCurrentChange"
                    />
                </div>
            </el-card>
        </div>

        <!-- 详情对话框 -->
        <el-dialog 
            v-model="detailDialogVisible" 
            title="故障详情" 
            width="600px"
            @close="closeDetailDialog"
        >
            <div v-if="selectedAlert" class="detail-content">
                <el-descriptions :column="2" border>
                    <el-descriptions-item label="告警ID">{{ selectedAlert.id }}</el-descriptions-item>
                    <el-descriptions-item label="告警类型">{{ selectedAlert.type }}</el-descriptions-item>
                    <el-descriptions-item label="描述" span="2">{{ selectedAlert.description }}</el-descriptions-item>
                    <el-descriptions-item label="位置">{{ selectedAlert.location }}</el-descriptions-item>
                    <el-descriptions-item label="切片">{{ selectedAlert.slice }}</el-descriptions-item>
                    <el-descriptions-item label="发生时间" span="2">{{ selectedAlert.createTime }}</el-descriptions-item>
                    <el-descriptions-item label="当前状态" span="2">
                        <el-tag :type="getStatusTagType(selectedAlert.status)">
                            {{ selectedAlert.status }}
                        </el-tag>
                    </el-descriptions-item>
                </el-descriptions>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="detailDialogVisible = false">关闭</el-button>
                    <el-button 
                        type="primary" 
                        @click="updateStatusFromDialog('处理中')"
                        :disabled="selectedAlert?.status === '处理中' || selectedAlert?.status === '已解决'"
                    >
                        标记为处理中
                    </el-button>
                    <el-button 
                        type="success" 
                        @click="updateStatusFromDialog('已解决')"
                        :disabled="selectedAlert?.status === '已解决'"
                    >
                        标记为已解决
                    </el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
    Warning, 
    InfoFilled, 
    SuccessFilled, 
    Operation, 
    Refresh,
    TrendCharts 
} from '@element-plus/icons-vue';

// 类型定义
interface Alert {
    id: string;
    type: string;
    description: string;
    severity: '高' | '中' | '低';
    location: string;
    createTime: string;
    status: '待处理' | '处理中' | '已解决';
    slice: string;
}

// 响应式数据
const loading = ref(false);
const alerts = ref<Alert[]>([]);
const filterStatus = ref('');
const filterSeverity = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const detailDialogVisible = ref(false);
const selectedAlert = ref<Alert | null>(null);

// 统计数据
const stats = reactive({
    delayUp: 0,    // 延迟上升
    interrupt: 0,  // 中断
    other: 0,      // 其他
    total: 0
});

// 计算属性 - 过滤后的告警
const filteredAlerts = computed(() => {
    let filtered = alerts.value;
    
    if (filterStatus.value) {
        filtered = filtered.filter(alert => alert.status === filterStatus.value);
    }
    
    if (filterSeverity.value) {
        filtered = filtered.filter(alert => alert.severity === filterSeverity.value);
    }
    
    return filtered;
});

// 计算属性 - 总数
const totalCount = computed(() => filteredAlerts.value.length);

// 方法
const getSeverityTagType = (severity: string) => {
    switch (severity) {
        case '高': return 'danger';
        case '中': return 'warning';
        case '低': return 'success';
        default: return '';
    }
};

const getStatusTagType = (status: string) => {
    switch (status) {
        case '待处理': return 'danger';
        case '处理中': return 'warning';
        case '已解决': return 'success';
        default: return '';
    }
};

const updateStatus = async (alert: Alert, newStatus: string) => {
    try {
        await ElMessageBox.confirm(
            `确定要将告警 ${alert.id} 状态更新为 "${newStatus}" 吗？`,
            '确认操作',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
            }
        );
        
        // 更新状态
        alert.status = newStatus as Alert['status'];
        updateStats();
        ElMessage.success('状态更新成功');
    } catch {
        ElMessage.info('已取消操作');
    }
};

const clearFilters = () => {
    filterStatus.value = '';
    filterSeverity.value = '';
    ElMessage.success('筛选条件已清空');
};

const updateStatusFromDialog = async (newStatus: string) => {
    if (selectedAlert.value) {
        try {
            await ElMessageBox.confirm(
                `确定要将告警 ${selectedAlert.value.id} 状态更新为 "${newStatus}" 吗？`,
                '确认操作',
                {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning',
                }
            );
            
            // 更新状态
            selectedAlert.value.status = newStatus as Alert['status'];
            updateStats();
            ElMessage.success('状态更新成功');
            detailDialogVisible.value = false;
        } catch {
            ElMessage.info('已取消操作');
        }
    }
};

const viewDetail = (alert: Alert) => {
    selectedAlert.value = alert;
    detailDialogVisible.value = true;
};

const closeDetailDialog = () => {
    selectedAlert.value = null;
    detailDialogVisible.value = false;
};

const refreshData = async () => {
    loading.value = true;
    try {
        await loadAlerts();
        ElMessage.success('数据刷新成功');
    } catch (error) {
        ElMessage.error('数据刷新失败');
    } finally {
        loading.value = false;
    }
};

const handleSizeChange = (size: number) => {
    pageSize.value = size;
    currentPage.value = 1;
};

const handleCurrentChange = (page: number) => {
    currentPage.value = page;
};

const loadAlerts = async () => {
    try {
        const response = await fetch('/mock/alert.json');
        const data = await response.json();
        alerts.value = data.currentIssues || [];
        updateStats();
    } catch (error) {
        console.error('加载告警数据失败:', error);
        ElMessage.error('加载告警数据失败');
    }
};

const updateStats = () => {
    const counts = { delayUp: 0, interrupt: 0, other: 0 };
    
    alerts.value.forEach(alert => {
        if (alert.status !== '已解决') {
            if (alert.type.includes('延迟')) {
                counts.delayUp++;
            } else if (alert.type.includes('中断')) {
                counts.interrupt++;
            } else {
                counts.other++;
            }
        }
    });
    
    stats.delayUp = counts.delayUp;
    stats.interrupt = counts.interrupt;
    stats.other = counts.other;
    stats.total = counts.delayUp + counts.interrupt + counts.other;
};

// 生命周期
onMounted(() => {
    loadAlerts();
});
</script>

<style scoped>
.fault-handling-container {
    padding: 20px;
    background-color: #f5f7fa;
    min-height: calc(100vh - 70px);
}

/* 统计卡片样式 */
.stats-section {
    margin-bottom: 20px;
}

.stats-card {
    height: 100px;
}

.stats-content {
    display: flex;
    align-items: center;
    height: 100%;
    padding: 0 10px;
}

.stats-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    color: white;
}

.stats-icon.delay {
    background: linear-gradient(135deg, #ffa502, #ff9500);
}

.stats-icon.interrupt {
    background: linear-gradient(135deg, #ff4757, #ff3838);
}

.stats-icon.other {
    background: linear-gradient(135deg, #2ed573, #1dd1a1);
}

.stats-icon.total {
    background: linear-gradient(135deg, #5352ed, #3742fa);
}

.stats-text {
    flex: 1;
}

.stats-number {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
    line-height: 1;
}

.stats-label {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
}

/* 表格样式 */
.table-section {
    margin-bottom: 20px;
}

.table-card {
    padding: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ebeef5;
}

.card-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
}

.header-controls {
    display: flex;
    align-items: center;
}

.pagination-container {
    margin-top: 20px;
    text-align: right;
}

/* 详情对话框样式 */
.detail-content {
    padding: 10px 0;
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .card-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }
    
    .header-controls {
        width: 100%;
        justify-content: flex-start;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .stats-content {
        padding: 0 5px;
    }
    
    .stats-icon {
        margin-right: 10px;
    }
}
</style>
