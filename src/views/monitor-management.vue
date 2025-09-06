<template>
    <div class="monitor-management-container">
        <!-- 主要内容区域 -->
        <el-row :gutter="20" class="main-content">
            <!-- 左侧：地图和拓扑视图 -->
            <el-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
                <el-card shadow="hover" class="map-topology-card" style="height: 800px;">
                    <div class="card-header">
                        <h3 class="card-title">拓扑视图</h3>
                        <div class="view-controls">
                            <el-radio-group v-model="viewMode" size="small">
                                <el-radio-button value="map">地图视图</el-radio-button>
                                <el-radio-button value="topology">拓扑视图</el-radio-button>
                            </el-radio-group>
                        </div>
                    </div>
                    <div class="view-container" style="height: calc(100% - 60px);">
                        <!-- 地图视图 -->
                        <div v-if="viewMode === 'map'" class="map-view" style="width: 100%; height: 100%;">
                            <v-chart 
                                v-if="topologyData" 
                                class="chart" 
                                :option="mapOptions" 
                                style="width: 100%; height: 100%;"
                            />
                            <div v-else class="map-placeholder">
                                <el-icon size="60"><Location /></el-icon>
                                <p>请上传拓扑配置文件以显示地理视图</p>
                            </div>
                        </div>
                        <!-- 拓扑视图 -->
                        <div v-else class="topology-view" style="width: 100%; height: 100%;">
                            <v-chart 
                                v-if="topologyData" 
                                class="chart" 
                                :option="topologyOptions" 
                                style="width: 100%; height: 100%;"
                            />
                            <div v-else class="topology-placeholder">
                                <el-icon size="60"><Connection /></el-icon>
                                <p>请上传拓扑配置文件</p>
                                
                                <!-- 显示已上传的拓扑文件列表 -->
                                <div v-if="uploadedFiles.length > 0" class="uploaded-files">
                                    <h4>已上传的拓扑文件:</h4>
                                    <el-table :data="uploadedFiles" size="small" style="width: 100%; max-width: 500px; margin: 20px auto;">
                                        <el-table-column prop="name" label="文件名" />
                                        <el-table-column prop="upload_time" label="上传时间" width="150" />
                                        <el-table-column label="操作" width="80">
                                            <template #default="scope">
                                                <el-button size="small" @click="loadExistingTopology(scope.row.path)">加载</el-button>
                                            </template>
                                        </el-table-column>
                                    </el-table>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>

            <!-- 右侧：配置和部署 -->
            <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
                <div class="right-panel">
                    <!-- 拓扑配置 -->
                    <el-card shadow="hover" class="config-card" style="margin-bottom: 20px;">
                        <div class="card-header">
                            <h3 class="card-title">拓扑数据文件</h3>
                        </div>
                        <div class="config-content">
                            <el-form :model="topologyConfig" label-width="100px" size="small">
                                <el-form-item label="配置文件">
                                    <el-upload
                                        class="upload-demo"
                                        drag
                                        action="#"
                                        :auto-upload="false"
                                        :on-change="handleFileChange"
                                        accept=".json,.yaml,.yml"
                                    >
                                        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                                        <div class="el-upload__text">
                                            拖拽文件到此处或<em>点击上传</em>
                                        </div>
                                        <template #tip>
                                            <div class="el-upload__tip">
                                                支持 json/yaml 格式的拓扑配置文件
                                            </div>
                                        </template>
                                    </el-upload>
                                </el-form-item>
                                
                                <el-form-item label="文件路径">
                                    <el-input
                                        v-model="topologyConfig.filePath"
                                        placeholder="请输入拓扑数据文件路径"
                                        clearable
                                    />
                                </el-form-item>
                                
                                <el-form-item>
                                    <el-button type="primary" @click="startDeployment" :loading="deploymentLoading">
                                        开始部署
                                    </el-button>
                                    <el-button @click="validateConfig">验证配置</el-button>
                                </el-form-item>
                            </el-form>
                        </div>
                    </el-card>

                    <!-- 部署进度 -->
                    <el-card shadow="hover" class="deployment-card">
                        <div class="card-header">
                            <h3 class="card-title">部署安装过程</h3>
                        </div>
                        <div class="deployment-content">
                            <el-steps :active="deploymentStep" direction="vertical" size="small">
                                <el-step 
                                    v-for="(step, index) in deploymentSteps" 
                                    :key="index"
                                    :title="step.title" 
                                    :description="step.description"
                                    :status="step.status"
                                />
                            </el-steps>
                            
                            <!-- 部署日志 -->
                            <div class="deployment-logs" v-if="deploymentLogs.length > 0">
                                <h4>部署日志</h4>
                                <div class="log-container">
                                    <div 
                                        v-for="(log, index) in deploymentLogs" 
                                        :key="index"
                                        :class="['log-item', log.type]"
                                    >
                                        <span class="log-time">{{ log.time }}</span>
                                        <span class="log-message">{{ log.message }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </el-card>
                </div>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Location, Connection, UploadFilled } from '@element-plus/icons-vue';

// 导入ECharts
import { use, registerMap } from 'echarts/core';
import { BarChart, LineChart, PieChart, MapChart, ScatterChart, LinesChart, GraphChart } from 'echarts/charts';
import {
    GridComponent,
    TooltipComponent,
    LegendComponent,
    TitleComponent,
    VisualMapComponent,
    ToolboxComponent,
    DataZoomComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';
import chinaMap from '@/utils/china';

// 注册ECharts组件
use([
    CanvasRenderer,
    BarChart,
    GridComponent,
    LineChart,
    PieChart,
    TooltipComponent,
    LegendComponent,
    TitleComponent,
    VisualMapComponent,
    ToolboxComponent,
    DataZoomComponent,
    MapChart,
    ScatterChart,
    LinesChart,
    GraphChart,
]);
registerMap('china', chinaMap);

// 响应式数据
const viewMode = ref('map');
const deploymentLoading = ref(false);
const deploymentStep = ref(0);
const topologyData = ref(null);  // 存储拓扑数据
const uploadedFiles = ref([]);   // 存储已上传的文件列表

// 地图中心和缩放
const mapCenter = ref([104, 35]);
const mapZoom = ref(1.5);

// 拓扑配置 - 移除了environment字段
const topologyConfig = reactive({
    filePath: ''
});

// 部署步骤
const deploymentSteps = ref([
    {
        title: '配置验证',
        description: '验证拓扑配置文件格式和内容',
        status: 'wait'
    },
    {
        title: '环境准备',
        description: '准备部署环境和依赖',
        status: 'wait'
    },
    {
        title: '拓扑部署',
        description: '部署网络拓扑结构',
        status: 'wait'
    },
    {
        title: '服务启动',
        description: '启动相关网络服务',
        status: 'wait'
    },
    {
        title: '连接测试',
        description: '测试网络连接和服务状态',
        status: 'wait'
    },
    {
        title: '部署完成',
        description: '部署成功，系统正常运行',
        status: 'wait'
    }
]);

// 部署日志
const deploymentLogs = ref([]);

// 方法
const handleFileChange = async (file) => {
    console.log('选择文件:', file.name);
    
    try {
        // 创建FormData对象
        const formData = new FormData();
        formData.append('file', file.raw);
        
        // 上传文件到后端
        const response = await fetch('http://localhost:5000/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('文件上传失败');
        }
        
        const result = await response.json();
        topologyConfig.filePath = result.file_path;
        
        // 读取文件内容并渲染拓扑图
        await loadTopologyData(result.file_path);
        
        ElMessage.success('文件上传成功并已加载拓扑图');
    } catch (error) {
        console.error('文件上传失败:', error);
        ElMessage.error('文件上传失败: ' + error.message);
    }
};

// 加载和显示拓扑数据
const loadTopologyData = async (filePath) => {
    try {
        // 从后端获取文件内容
        const response = await fetch(`http://localhost:5000/api/files?path=${encodeURIComponent(filePath)}`);
        if (!response.ok) {
            throw new Error('获取文件内容失败');
        }
        
        const data = await response.json();
        topologyData.value = data;
        
        console.log('拓扑数据加载成功:', data);
        console.log('节点数据:', data.nodes);
        console.log('连接数据:', data.links);
        
        // 切换到拓扑视图以便查看结果
        viewMode.value = 'topology';
        
    } catch (error) {
        console.error('加载拓扑数据失败:', error);
        ElMessage.error('加载拓扑数据失败: ' + error.message);
    }
};

// 地图视图选项 - 参考dashboard.vue的实现
const mapOptions = computed(() => {
    console.log('mapOptions computed, topologyData:', topologyData.value);
    
    if (!topologyData.value) {
        return {
            title: {
                text: '请上传拓扑配置文件',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#999',
                    fontSize: 16
                }
            }
        };
    }

    const { nodes, links } = topologyData.value;
    console.log('地图视图 - 节点数据:', nodes);
    console.log('地图视图 - 连接数据:', links);

    if (!nodes || nodes.length === 0) {
        return {
            title: {
                text: '暂无网络拓扑数据',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#ffa726',
                    fontSize: 16
                }
            }
        };
    }

    // 处理连接数据
    const processConnections = (links, nodes) => {
        const allConnections = [];
        
        if (!links || links.length === 0) {
            return allConnections;
        }
        
        links.forEach(link => {
            const sourceNode = nodes.find(n => n.id === link.source);
            const targetNode = nodes.find(n => n.id === link.target);
            
            if (sourceNode && targetNode) {
                allConnections.push({
                    name: `${sourceNode.name}-${targetNode.name}`,
                    coords: [sourceNode.location, targetNode.location]
                });
            }
        });
        
        return allConnections;
    };

    const processedConnections = processConnections(links, nodes);

    return {
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                if (params.seriesType === 'lines') {
                    return `<div style="font-weight: bold;">${params.data.name}</div>`;
                } else if (params.seriesType === 'scatter') {
                    return `<div style="font-weight: bold;">${params.data.name}</div>`;
                }
                return params.name;
            }
        },
        geo: {
            map: 'china',
            center: mapCenter.value,
            zoom: mapZoom.value,
            roam: true,
            scaleLimit: {
                min: 0.3,
                max: 8
            },
            layoutCenter: ['50%', '50%'],
            layoutSize: '70%',
            itemStyle: {
                areaColor: '#f0f0f0',
                borderColor: '#d9d9d9',
                borderWidth: 1.5
            }
        },
        series: [
            // 连接线
            {
                name: '网络连接',
                type: 'lines',
                coordinateSystem: 'geo',
                data: processedConnections.map((conn) => ({
                    name: conn.name,
                    coords: conn.coords,
                    lineStyle: {
                        color: '#52c41a',
                        width: 2.5,
                        type: 'solid'
                    }
                }))
            },
            // 网络节点
            {
                name: '网络节点',
                type: 'scatter',
                coordinateSystem: 'geo',
                symbol: 'circle',
                symbolSize: 14,
                itemStyle: {
                    color: '#595959',
                    borderColor: '#ffffff',
                    borderWidth: 2
                },
                data: nodes.map((node) => ({
                    name: node.name,
                    value: [node.location[0], node.location[1], node.name]
                })),
                label: {
                    show: true,
                    position: 'right',
                    formatter: '{b}',
                    fontSize: 12,
                    color: '#333',
                    fontWeight: 'bold'
                }
            }
        ]
    };
});

// 拓扑视图选项 - 参考dashboard.vue的实现
const topologyOptions = computed(() => {
    if (!topologyData.value) {
        return {
            title: {
                text: '请上传拓扑配置文件',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#999',
                    fontSize: 16
                }
            }
        };
    }

    const { nodes: topologyNodes, links: topologyLinks } = topologyData.value;

    if (!topologyNodes || topologyNodes.length === 0) {
        return {
            title: {
                text: '暂无拓扑数据',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#999',
                    fontSize: 16
                }
            }
        };
    }

    // 转换节点数据
    const nodes = topologyNodes.map((node, index) => ({
        id: node.id,
        name: node.name,
        symbolSize: 40,
        itemStyle: {
            color: '#3498DB'
        },
        label: {
            show: true,
            color: '#2c3e50',
            fontSize: 12
        }
    }));

    // 转换连接数据
    const links = [];
    if (topologyLinks && topologyLinks.length > 0) {
        topologyLinks.forEach(link => {
            if (link.source && link.target) {
                links.push({
                    source: link.source,
                    target: link.target,
                    name: `${link.source}-${link.target}`,
                    lineStyle: {
                        color: '#52c41a',
                        width: 3,
                        type: 'solid'
                    }
                });
            }
        });
    }

    return {
        title: {
            text: '网络拓扑图',
            left: 15,
            top: 15,
            textStyle: {
                color: '#2c3e50',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },
        backgroundColor: '#FAFAFA',
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                if (params.dataType === 'node') {
                    return `<strong>${params.data.name}</strong>`;
                } else if (params.dataType === 'edge') {
                    return `<div style="font-weight: bold;">${params.data.name}</div>`;
                }
                return '';
            }
        },
        series: [{
            name: '网络拓扑',
            type: 'graph',
            layout: 'force',
            data: nodes,
            links: links,
            roam: true,
            draggable: true,
            itemStyle: {
                borderColor: '#fff',
                borderWidth: 2
            },
            emphasis: {
                focus: 'adjacency'
            },
            force: {
                repulsion: 2000,
                gravity: 0.1,
                edgeLength: [80, 200],
                layoutAnimation: true,
                friction: 0.6
            },
            animationDuration: 1000,
            animationEasing: 'cubicOut'
        }]
    };
});

// 获取已上传文件列表
const loadUploadedFiles = async () => {
    try {
        const response = await fetch('http://localhost:5000/api/files');
        if (response.ok) {
            const files = await response.json();
            uploadedFiles.value = files;
        }
    } catch (error) {
        console.error('获取文件列表失败:', error);
    }
};

// 加载已存在的拓扑文件
const loadExistingTopology = async (filePath) => {
    try {
        topologyConfig.filePath = filePath;
        await loadTopologyData(filePath);
        ElMessage.success('拓扑文件加载成功');
    } catch (error) {
        console.error('加载拓扑文件失败:', error);
        ElMessage.error('加载拓扑文件失败: ' + error.message);
    }
};

// 删除拓扑文件
const deleteTopologyFile = async (filePath) => {
    try {
        await ElMessageBox.confirm('确定要删除这个拓扑文件吗？', '确认删除', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        });
        
        const response = await fetch(`http://localhost:5000/api/files?path=${encodeURIComponent(filePath)}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('删除文件失败');
        }
        
        // 刷新文件列表
        await loadUploadedFiles();
        
        // 如果删除的是当前加载的拓扑，清空显示
        if (topologyConfig.filePath === filePath) {
            topologyData.value = null;
            topologyConfig.filePath = '';
        }
        
        ElMessage.success('文件删除成功');
    } catch (error) {
        if (error !== 'cancel') {
            console.error('删除文件失败:', error);
            ElMessage.error('删除文件失败: ' + error.message);
        }
    }
};

const validateConfig = async () => {
    if (!topologyConfig.filePath) {
        ElMessage.warning('请先选择或输入拓扑配置文件');
        return;
    }
    
    try {
        // 调用后端验证API
        const response = await fetch('http://localhost:5000/api/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_path: topologyConfig.filePath
            })
        });
        
        if (!response.ok) {
            throw new Error('配置验证失败');
        }
        
        const result = await response.json();
        
        // 验证成功后加载拓扑数据
        await loadTopologyData(topologyConfig.filePath);
        
        ElMessage.success('配置验证通过');
        addDeploymentLog('info', '配置文件验证通过');
        
    } catch (error) {
        console.error('配置验证失败:', error);
        ElMessage.error('配置验证失败: ' + error.message);
        addDeploymentLog('error', '配置验证失败: ' + error.message);
    }
};

const startDeployment = async () => {
    if (!topologyConfig.filePath) {
        ElMessage.warning('请先选择或输入拓扑配置文件');
        return;
    }
    
    deploymentLoading.value = true;
    deploymentStep.value = 0;
    deploymentLogs.value = [];
    
    // 重置所有步骤状态
    deploymentSteps.value.forEach(step => {
        step.status = 'wait';
    });
    
    try {
        // 调用后端部署API
        const response = await fetch('http://localhost:5000/api/deploy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_path: topologyConfig.filePath
            })
        });
        
        if (!response.ok) {
            throw new Error('启动部署失败');
        }
        
        const result = await response.json();
        const taskId = result.task_id;
        
        addDeploymentLog('info', '部署任务已启动: ' + taskId);
        
        // 轮询部署状态
        const pollInterval = setInterval(async () => {
            try {
                const statusResponse = await fetch(`http://localhost:5000/api/deployment/${taskId}`);
                if (statusResponse.ok) {
                    const statusData = await statusResponse.json();
                    
                    // 更新步骤状态
                    statusData.steps.forEach((step, index) => {
                        if (deploymentSteps.value[index]) {
                            deploymentSteps.value[index].status = step.status;
                            deploymentSteps.value[index].description = step.description;
                        }
                    });
                    
                    // 更新当前步骤
                    deploymentStep.value = statusData.steps.findIndex(s => s.status === 'process');
                    if (deploymentStep.value === -1) {
                        deploymentStep.value = statusData.steps.length;
                    }
                    
                    // 添加新日志
                    if (statusData.logs && statusData.logs.length > deploymentLogs.value.length) {
                        statusData.logs.slice(deploymentLogs.value.length).forEach(log => {
                            deploymentLogs.value.push({
                                time: new Date(log.timestamp).toLocaleTimeString(),
                                message: log.message,
                                type: log.level
                            });
                        });
                    }
                    
                    // 检查是否完成
                    if (statusData.status === 'completed') {
                        clearInterval(pollInterval);
                        deploymentLoading.value = false;
                        ElMessage.success('部署完成！');
                        addDeploymentLog('success', '所有部署步骤已完成');
                    } else if (statusData.status === 'failed') {
                        clearInterval(pollInterval);
                        deploymentLoading.value = false;
                        ElMessage.error('部署失败！');
                        addDeploymentLog('error', '部署过程中出现错误');
                    }
                }
            } catch (error) {
                console.error('获取部署状态失败:', error);
            }
        }, 1000);
        
        // 设置超时
        setTimeout(() => {
            clearInterval(pollInterval);
            if (deploymentLoading.value) {
                deploymentLoading.value = false;
                ElMessage.warning('部署超时，请检查后端服务');
            }
        }, 300000); // 5分钟超时
        
    } catch (error) {
        deploymentLoading.value = false;
        console.error('部署失败:', error);
        ElMessage.error('部署失败: ' + error.message);
        addDeploymentLog('error', '部署启动失败: ' + error.message);
    }
};

const addDeploymentLog = (type, message) => {
    const now = new Date();
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    
    deploymentLogs.value.push({
        type,
        time,
        message
    });
};

onMounted(() => {
    // 初始化地图和拓扑视图
    initViews();
    // 加载已上传的文件列表
    loadUploadedFiles();
});

const initViews = () => {
    // 使用v-chart组件自动处理视图初始化
    console.log('使用v-chart初始化地图和拓扑视图...');
};
</script>

<style scoped>
.monitor-management-container {
    padding: 20px;
    background-color: #f5f7fa;
    min-height: calc(100vh - 70px);
}

.tabs-container {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.management-tabs {
    width: 100%;
}

.tab-content {
    margin-top: 20px;
}

.main-content {
    height: 800px;
}

.map-topology-card {
    height: 100%;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 20px;
    border-bottom: 1px solid #ebeef5;
    margin-bottom: 20px;
}

.card-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
}

.view-controls {
    display: flex;
    align-items: center;
}

.view-container {
    position: relative;
    width: 100%;
}

.map-view, .topology-view {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f8f9fa;
    border-radius: 6px;
    border: 1px dashed #d9d9d9;
}

.map-placeholder, .topology-placeholder {
    text-align: center;
    color: #909399;
}

.map-placeholder p, .topology-placeholder p {
    margin-top: 15px;
    font-size: 14px;
}

.right-panel {
    height: 800px;
    overflow-y: auto;
}

.config-card, .deployment-card {
    height: auto;
}

.config-content {
    padding: 10px 0;
}

.deployment-content {
    padding: 10px 0;
}

.deployment-logs {
    margin-top: 20px;
    border-top: 1px solid #ebeef5;
    padding-top: 15px;
}

.deployment-logs h4 {
    margin: 0 0 10px 0;
    font-size: 14px;
    color: #606266;
}

.log-container {
    max-height: 200px;
    overflow-y: auto;
    background: #f8f9fa;
    border-radius: 4px;
    padding: 10px;
}

.log-item {
    display: flex;
    margin-bottom: 8px;
    font-size: 12px;
    line-height: 1.4;
}

.log-time {
    color: #909399;
    margin-right: 10px;
    min-width: 60px;
}

.log-message {
    flex: 1;
}

.log-item.success .log-message {
    color: #67c23a;
}

.log-item.error .log-message {
    color: #f56c6c;
}

.log-item.info .log-message {
    color: #409eff;
}

.log-item.warning .log-message {
    color: #e6a23c;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .monitor-management-container {
        padding: 10px;
    }
    
    .main-content {
        height: auto;
    }
    
    .map-topology-card {
        height: 400px;
        margin-bottom: 20px;
    }
    
    .right-panel {
        height: auto;
    }
}

/* 上传组件样式调整 */
:deep(.el-upload-dragger) {
    width: 100%;
    height: 120px;
}

:deep(.el-steps--vertical .el-step__main) {
    padding-left: 10px;
}
</style>
