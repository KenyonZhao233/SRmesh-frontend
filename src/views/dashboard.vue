<template>
    <div class="dashboard-container">
        <!-- 切片筛选条 -->
        <div class="slice-filter-bar mgb20">
            <div class="filter-content">
                <div class="stats-section">
                    <div class="slice-stats-group">
                        <div class="stats-item">
                            <span class="stats-number">{{ sliceStats.total }}</span>
                            <span class="stats-label">总切片数</span>
                        </div>
                        <div class="stats-item">
                            <span class="stats-number active">{{ sliceStats.active }}</span>
                            <span class="stats-label">活跃切片</span>
                        </div>
                        <div class="stats-item">
                            <span class="stats-number warning">{{ sliceStats.warning }}</span>
                            <span class="stats-label">空闲切片</span>
                        </div>
                    </div>
                    <!-- 切片可用性色块组 -->
                    <div class="availability-stats-group">
                        <div class="availability-title">全网切片可用性：</div>
                        <div class="availability-items">
                            <div class="availability-item available">
                                <div class="availability-number">{{ networkAvailability.available }}</div>
                                <div class="availability-label">可用</div>
                            </div>
                            <div class="availability-item exception">
                                <div class="availability-number">{{ networkAvailability.exception }}</div>
                                <div class="availability-label">异常</div>
                            </div>
                            <div class="availability-item unavailable">
                                <div class="availability-number">{{ networkAvailability.unavailable }}</div>
                                <div class="availability-label">不可用</div>
                            </div>
                            <div class="availability-item unknown">
                                <div class="availability-number">{{ networkAvailability.unknown }}</div>
                                <div class="availability-label">未知</div>
                            </div>
                            <div class="availability-item total">
                                <div class="availability-number">{{ networkAvailability.total }}</div>
                                <div class="availability-label">合计</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="filter-section">
                    <span class="filter-label">切片组切换</span>
                    <el-select
                        v-model="selectedSliceGroup"
                        placeholder="选择切片组"
                        @change="handleSliceGroupChange"
                        size="small"
                        class="filter-select"
                    >
                        <el-option 
                            v-for="group in sliceGroups" 
                            :key="group.value"
                            :label="group.label" 
                            :value="group.value" 
                        />
                    </el-select>
                </div>
            </div>
        </div>

        <el-row :gutter="20" class="mgb20 responsive-row chart-row">
              <el-col :xs="24" :sm="24" :md="17" :lg="17" :xl="17">
                <el-card shadow="hover" class="responsive-card chart-card map-slice-card">
                    <div class="card-header">
                        <p class="card-header-title">切片延迟</p>
                        <p class="card-header-desc">切片拓扑</p>
                    </div>
                    <div class="chart-container">
                        <!-- 左半部分：切片可视化 -->
                        <div class="left-component">
                            <div class="slice-visualizer">
                                <div class="slice-header">
                                    <h3>切片可视化</h3>
                                    <p>选择要查看的网络切片</p>
                                </div>
                                <div class="zoom-controls">
                                    <button @click="zoomIn" class="zoom-btn">+</button>
                                    <button @click="zoomOut" class="zoom-btn">-</button>
                                    <button @click="resetZoom" class="zoom-btn">重置</button>
                                </div>
                                <div class="slice-stack-container" @wheel="handleZoom">
                                    <div class="slice-stack" :style="{ transform: `scale(${zoomLevel})` }">
                                        <div 
                                            v-for="(slice, index) in displayedSlices" 
                                            :key="slice.id"
                                            :class="['slice-layer', { 'active': selectedSlice === slice.id }]"
                                            :style="getSliceStyle(index)"
                                            @click="selectSlice(slice.id)"
                                            @mouseenter="hoveredSlice = slice.id"
                                            @mouseleave="hoveredSlice = null"
                                        >
                                            <div class="slice-content">
                                                <div class="slice-name">{{ slice.name }}</div>
                                            </div>
                                            <!-- 悬浮提示 - 只显示名字 -->
                                            <div 
                                                v-if="hoveredSlice === slice.id" 
                                                class="slice-tooltip"
                                            >
                                                <div class="tooltip-title">{{ slice.name }}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="selected-slice-info" v-if="selectedSliceInfo">
                                    <h4>当前选择: {{ selectedSliceInfo.name }}</h4>
                                </div>
                            </div>
                        </div>
                        <!-- 右半部分：地图/拓扑 -->
                        <div class="right-component">
                            <v-chart 
                                class="map-chart" 
                                :option="viewMode === 'geographic' ? enhancedMapOptions : topologyOptions" 
                                @click="handleMapClick"
                                :key="viewMode"
                            />
                            <div class="view-mode-switcher">
                                <div class="switcher-buttons">
                                    <el-button 
                                        :type="viewMode === 'geographic' ? 'primary' : 'default'"
                                        size="small"
                                        @click="viewMode = 'geographic'"
                                        class="switcher-btn"
                                    >
                                        地理
                                    </el-button>
                                    <el-button 
                                        :type="viewMode === 'topology' ? 'primary' : 'default'"
                                        size="small"
                                        @click="viewMode = 'topology'"
                                        class="switcher-btn"
                                    >
                                        拓扑
                                    </el-button>
                                </div>
                                <div class="switcher-description">
                                    <span class="description-text">
                                        {{ viewMode === 'geographic' ? '基于地理的网络视图' : '抽象网络拓扑结构图' }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :xs="24" :sm="24" :md="7" :lg="7" :xl="7">
                <el-card shadow="hover" class="responsive-card chart-card">
                    <div class="card-header">
                        <p class="card-header-title">链路时延</p>
                        <p class="card-header-desc">24小时实时网络时延趋势</p>
                        <div v-if="delayDataError" class="retry-section">
                            <el-button 
                                type="primary" 
                                size="small" 
                                @click="retryLoadDelayData"
                                :loading="delayDataLoading"
                            >
                                重试连接
                            </el-button>
                        </div>
                    </div>
                    <v-chart class="timeline-chart" :option="timelineOptions" />
                </el-card>
            </el-col>
        </el-row>
        <el-row :gutter="5" class="mgb20 responsive-row table-row">
            <el-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
                <el-card shadow="hover" class="responsive-card table-card">
                    <div class="card-header">
                        <p class="card-header-title">当前问题</p>
                        <p class="card-header-desc">当前网络存在的问题</p>
                    </div>
                    <div class="table-container">
                        <el-table :data="currentIssuesData" style="width: 100%" class="responsive-table">
                            <el-table-column prop="id" label="问题ID" min-width="80" />
                            <el-table-column prop="type" label="问题类型" min-width="100">
                                <template #default="scope">
                                    <el-tag :type="getIssueTypeColor(scope.row.type)">
                                        {{ scope.row.type }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="description" label="问题描述" min-width="200"/>
                            <el-table-column prop="severity" label="严重程度" min-width="100">
                                <template #default="scope">
                                    <el-tag :type="getSeverityColor(scope.row.severity)">
                                        {{ scope.row.severity }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="slice" label="所属切片" min-width="120" />
                            <el-table-column prop="location" label="位置" min-width="120" />
                            <el-table-column prop="createTime" label="发现时间" min-width="180" />
                            <el-table-column prop="status" label="状态" min-width="80">
                                <template #default="scope">
                                    <el-tag :type="getStatusColor(scope.row.status)">
                                        {{ scope.row.status }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </el-card>
            </el-col>
            <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
                <el-card shadow="hover" class="responsive-card table-card">
                    <div class="card-header">
                        <div class="header-content">
                            <div class="header-left">
                                <p class="card-header-title">当前切片探测列表</p>
                                <p class="card-header-desc">{{ pingListData?.sliceName || '加载中...' }}网络连通性探测</p>
                            </div>
                            <div class="header-right" v-if="pingListData?.pingList">
                                <span class="ping-count">{{ pingListData.pingList.length }}对</span>
                            </div>
                        </div>
                    </div>
                    <div class="table-container">
                        <div v-if="isPingListLoading" class="loading-text">
                            加载探测数据中...
                        </div>
                        <div v-else-if="!pingListData?.pingList || pingListData.pingList.length === 0" class="empty-text">
                            暂无探测数据
                        </div>
                        <div v-else class="ping-list">
                            <div 
                                v-for="ping in pingListData.pingList" 
                                :key="ping.id"
                                class="ping-item"
                            >
                                <div class="ping-endpoints">
                                    <span class="ping-text">src: {{ ping.src }}, dst: {{ ping.dst }}, interval: {{ ping.interval }}, protocol: {{ ping.protocol }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
      
    </div>
</template>

<script setup lang="ts" name="dashboard">

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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import chinaMap from '@/utils/china';
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

// 如果有世界地图数据，也可以注册
// registerMap('world', worldMap);

// 响应式变量
const selectedRoute = ref('');

// 视图模式切换
const viewMode = ref('geographic'); // 'geographic' 或 'topology'

// 3D切片可视化相关变量
const selectedSlice = ref('physical-network'); // 默认选择物理网络，使用数据库中的实际名称
const hoveredSlice = ref(null);
const zoomLevel = ref(1);

// 网络拓扑数据
const networkTopology = ref(null);
const isTopologyLoading = ref(true);
const allSliceTopologies = ref({}); // 存储所有切片的拓扑数据

// 警报数据
const alertData = ref(null);
const isAlertLoading = ref(true);

// ping探测数据
const pingListData = ref({
    sliceName: "物理网",
    pingList: []
});
const isPingListLoading = ref(false);

// 实时时延数据
const delayDataLoading = ref(false);
const delayDataError = ref(null);
const realDelayData = ref(null);

// 缩放控制函数
const zoomIn = () => {
    if (zoomLevel.value < 2) {
        zoomLevel.value += 0.1;
    }
};

const zoomOut = () => {
    if (zoomLevel.value > 0.5) {
        zoomLevel.value -= 0.1;
    }
};

const resetZoom = () => {
    zoomLevel.value = 1;
};

const handleZoom = (event) => {
    event.preventDefault();
    if (event.deltaY < 0) {
        zoomIn();
    } else {
        zoomOut();
    }
};

// 网络切片数据 - 从配置文件动态加载
const networkSlices = ref([]);

// 加载切片配置
const loadSlicesConfiguration = async () => {
    try {
        const response = await fetch('/mock/total_slices.json');
        const data = await response.json();
        // 按优先级排序，确保物理网络在最前面
        networkSlices.value = data.slices.sort((a, b) => a.priority - b.priority);
        // 加载总切片数
        if (data.totalSlicesCount) {
            totalSlicesCount.value = data.totalSlicesCount;
        }
        console.log('切片配置加载成功:', networkSlices.value);
        console.log('总切片数:', totalSlicesCount.value);
    } catch (error) {
        console.error('加载切片配置失败:', error);
        // 如果加载失败，使用默认配置
    }
};


// 当前选择的切片信息
const selectedSliceInfo = computed(() => {
    return networkSlices.value.find(slice => slice.id === selectedSlice.value);
});

// 3D切片样式生成
const getSliceStyle = (index) => {
    // 反转索引，让第一个元素（物理网络）显示在最上面
    const reverseIndex = networkSlices.value.length - 1 - index;
    const zOffset = reverseIndex * 18; // 物理网络有最大的zOffset
    const yOffset = -reverseIndex * 8; // 物理网络有最大的yOffset
    const scale = 1 - reverseIndex * 0.01; // 轻微缩放差异
    
    return {
        transform: `translateZ(${zOffset}px) translateY(${yOffset}px) scale(${scale})`,
        zIndex: networkSlices.value.length - reverseIndex, // 物理网络有最高的zIndex
        backgroundColor: networkSlices.value[index]?.color + '20',
        borderColor: networkSlices.value[index]?.color
    };
};

// 选择切片
const selectSlice = (sliceId) => {
    selectedSlice.value = sliceId;
    // 切换到对应的网络拓扑
    switchSliceTopology(sliceId);
};

// 加载所有切片的网络拓扑数据
const loadAllSliceTopologies = async () => {
    try {
        isTopologyLoading.value = true;
        
        // 首先加载切片配置
        await loadSlicesConfiguration();
        
        // 根据配置文件动态生成文件列表
        const sliceFiles = networkSlices.value.map(slice => slice.filename);
        
        const topologies = {};
        
        // 并行加载所有切片拓扑文件
        const loadPromises = sliceFiles.map(async (filename) => {
            try {
                const response = await fetch(`/mock/slice/${filename}`);
                if (response.ok) {
                    const data = await response.json();
                    const sliceId = filename.replace('.json', '');
                    topologies[sliceId] = data;
                    console.log(`成功加载切片拓扑: ${sliceId}`, data);
                } else {
                    console.warn(`切片拓扑文件不存在: ${filename}`);
                }
            } catch (error) {
                console.error(`加载切片拓扑失败: ${filename}`, error);
            }
        });
        
        await Promise.all(loadPromises);
        
        allSliceTopologies.value = topologies;
        
        // 设置默认显示的拓扑为物理网络
        const physicalSlice = networkSlices.value.find(slice => slice.type === 'Physical');
        if (physicalSlice && topologies[physicalSlice.filename.replace('.json', '')]) {
            networkTopology.value = topologies[physicalSlice.filename.replace('.json', '')];
            console.log(`设置默认拓扑: ${physicalSlice.filename}`);
        } else if (Object.keys(topologies).length > 0) {
            // 如果没有物理网络，使用第一个可用的
            const currentSliceKey = Object.keys(topologies)[0];
            networkTopology.value = topologies[currentSliceKey];
            console.log(`设置默认拓扑: ${currentSliceKey}`);
        } else {
            // 如果没有切片文件，尝试加载原始文件作为回退
            await loadFallbackTopology();
        }
        
        // 设置默认选中的链路（默认显示所有链路）
        selectedRoute.value = 'all';
        console.log(`设置默认链路: ${selectedRoute.value}`);
        
        console.log('所有切片拓扑加载完成:', Object.keys(topologies));
        
    } catch (error) {
        console.error('加载切片拓扑数据失败:', error);
        await loadFallbackTopology();
    } finally {
        isTopologyLoading.value = false;
    }
};

// 回退加载原始网络拓扑文件
const loadFallbackTopology = async () => {
    try {
        const response = await fetch('/mock/network-topology.json');
        const data = await response.json();
        networkTopology.value = data;
        console.log('回退加载原始网络拓扑成功:', data);
        
        // 设置默认选中的链路为显示所有
        selectedRoute.value = 'all';
        console.log(`回退加载后设置默认链路: ${selectedRoute.value}`);
    } catch (error) {
        console.error('回退加载失败:', error);
        networkTopology.value = getDefaultTopology();
    }
};

// 根据选中的切片切换网络拓扑
const switchSliceTopology = (sliceId) => {
    const sliceKey = getSliceTopologyKey(sliceId);
    if (allSliceTopologies.value[sliceKey]) {
        networkTopology.value = allSliceTopologies.value[sliceKey];
        console.log(`切换到切片拓扑: ${sliceKey}`);
        
        // 切换切片时，设置默认显示所有链路
        selectedRoute.value = 'all';
        console.log(`切换切片后设置默认链路: ${selectedRoute.value}`);
        
        // 同时加载对应的ping探测数据
        loadPingListData(sliceId);
    } else {
        console.warn(`切片拓扑不存在: ${sliceKey}`);
    }
};

// 将切片ID映射到拓扑文件键名
const getSliceTopologyKey = (sliceId) => {
    // 从动态加载的切片配置中查找对应的文件名
    const slice = networkSlices.value.find(slice => slice.id === sliceId);
    if (slice && slice.filename) {
        return slice.filename.replace('.json', '');
    }
    
    // 如果没有找到，返回原始ID作为回退
    console.warn(`未找到切片ID ${sliceId} 对应的文件名`);
    return sliceId;
};

// 格式化链路名称显示 - 将ID转换为友好的城市名称
const formatLinkName = (linkId) => {
    if (!linkId || linkId === 'all') {
        return linkId;
    }
    
    // 解析链路ID (格式: "BJ001-SH002" 或 "0-1")
    const parts = linkId.split('-');
    if (parts.length !== 2) {
        return linkId; // 如果格式不正确，返回原始ID
    }
    
    const [sourceId, targetId] = parts;
    
    // 获取当前切片的拓扑数据
    const currentTopology = networkTopology.value;
    if (!currentTopology || !currentTopology.cities) {
        return linkId; // 如果没有拓扑数据，返回原始ID
    }
    
    // 查找对应的城市名称
    const sourceCity = currentTopology.cities.find(city => city.id === sourceId);
    const targetCity = currentTopology.cities.find(city => city.id === targetId);
    
    if (sourceCity && targetCity) {
        return `${sourceCity.name} ↔ ${targetCity.name}`;
    }
    
    // 如果找不到对应的城市，返回原始ID
    return linkId;
};

// 保留原来的函数名作为兼容
const loadNetworkTopology = loadAllSliceTopologies;

// 加载警报数据
const loadAlertData = async () => {
    try {
        isAlertLoading.value = true;
        const response = await fetch('/mock/alert.json');
        const data = await response.json();
        alertData.value = data;
        console.log('警报数据加载成功:', data);
    } catch (error) {
        console.error('加载警报数据失败:', error);
    } finally {
        isAlertLoading.value = false;
    }
};


// 加载当前切片的ping探测数据
const loadPingListData = async (sliceId) => {
    try {
        isPingListLoading.value = true;
        const sliceKey = getSliceTopologyKey(sliceId);
        const response = await fetch(`/mock/pinglist/${sliceKey}.json`);
        const data = await response.json();
        pingListData.value = data;
        console.log(`加载${sliceKey}切片探测数据成功:`, data);
    } catch (error) {
        console.error(`加载切片探测数据失败:`, error);
        pingListData.value = getDefaultPingListData();
    } finally {
        isPingListLoading.value = false;
    }
};

// 默认ping探测数据（备用）
const getDefaultPingListData = () => {
    return {
        sliceName: "默认切片",
        pingList: []
    };
};

// 加载实时时延数据
const loadDelayData = async (sliceFilter = null, linkFilter = null) => {
    try {
        delayDataLoading.value = true;
        delayDataError.value = null;
        
        const targetDate = '2025-01-01';
        const response = await fetch(`http://localhost:3001/api/delay-data/${targetDate}`);
        
        if (!response.ok) {
            throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        // 提取实际的数据数组
        let filteredData = result.data || [];
        
        // 根据切片过滤数据
        if (sliceFilter) {
            filteredData = filteredData.filter(item => item.slice === sliceFilter);
        }
        
        // 根据链路过滤数据 (src-dst组合)
        if (linkFilter) {
            const [src, dst] = linkFilter.split('-');
            if (src && dst) {
                filteredData = filteredData.filter(item => 
                    item.src === src && item.dst === dst
                );
            }
        }
        
        realDelayData.value = filteredData;
        console.log('实时时延数据加载成功:', result);
        console.log('过滤后数据条数:', realDelayData.value.length);
        console.log('过滤条件 - 切片:', sliceFilter, '链路:', linkFilter);
    } catch (error) {
        console.error('加载实时时延数据失败:', error);
        if (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED')) {
            delayDataError.value = '数据库服务未启动，请先启动数据库API服务';
        } else {
            delayDataError.value = error.message;
        }
        realDelayData.value = null;
    } finally {
        delayDataLoading.value = false;
    }
};

// 重试加载时延数据
const retryLoadDelayData = () => {
    loadDelayData();
};

// 获取默认拓扑数据（仅用作加载失败时的回退）
const getDefaultTopology = () => {
    return {
        cities: [],
        connections: [],
        error: true,
        message: '网络拓扑数据加载失败，请检查网络连接'
    };
};

// 增强的地图配置（支持缩放）
const enhancedMapOptions = computed(() => {
    if (!networkTopology.value) {
        return {
            title: {
                text: '加载网络拓扑中...',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#999',
                    fontSize: 16
                }
            }
        };
    }

    // 检查是否为错误状态
    if (networkTopology.value.error) {
        return {
            title: {
                text: networkTopology.value.message || '网络拓扑数据加载失败',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#ff4757',
                    fontSize: 16
                }
            }
        };
    }

    const { cities, connections } = networkTopology.value;

    // 检查数据是否为空
    if (!cities || cities.length === 0) {
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

    // 添加调试信息
    console.log('准备渲染地图，城市数据:', cities.length);
    console.log('连接数据:', connections?.length || 0);
    console.log('前3个城市:', cities.slice(0, 3));

    // 处理连接数据 - 根据points生成完全连通的网络
    const processConnections = (connections, cities) => {
        const allConnections = [];
        
        connections.forEach(conn => {
            const points = conn.points;
            
            // 如果只有两个点，直接连接
            if (points.length === 2) {
                const coords = points.map(pointIndex => {
                    const city = cities.find(c => c.id === pointIndex);
                    return city ? city.coord : [0, 0];
                });
                
                const cityNames = points.map(pointIndex => {
                    const city = cities.find(c => c.id === pointIndex);
                    return city ? city.id : `Node${pointIndex}`; // 使用ID而不是name
                });
                
                allConnections.push({
                    ...conn,
                    coords,
                    name: cityNames.join('-')
                });
            }
            // 如果有多个点，生成完全连通图（每两个点之间都有连接）
            else if (points.length > 2) {
                for (let i = 0; i < points.length; i++) {
                    for (let j = i + 1; j < points.length; j++) {
                        const point1 = points[i];
                        const point2 = points[j];
                        
                        const city1 = cities.find(c => c.id === point1);
                        const city2 = cities.find(c => c.id === point2);
                        
                        if (city1 && city2) {
                            allConnections.push({
                                ...conn,
                                id: `${conn.id}_${point1}_${point2}`,
                                coords: [city1.coord, city2.coord],
                                name: `${city1.id}-${city2.id}`, // 使用ID而不是name
                                points: [point1, point2] // 保持原始点信息
                            });
                        }
                    }
                }
            }
        });
        
        return allConnections;
    };

    const processedConnections = processConnections(connections, cities);

    // 节点防重叠处理函数
    const adjustNodePositions = (cities) => {
        const minDistance = 1.5; // 最小距离阈值（经纬度单位）
        const offsetRange = 0.3; // 偏移范围
        const adjustedCities = [...cities];

        for (let i = 0; i < adjustedCities.length; i++) {
            for (let j = i + 1; j < adjustedCities.length; j++) {
                const city1 = adjustedCities[i];
                const city2 = adjustedCities[j];
                
                // 计算两点间距离
                const dx = city1.coord[0] - city2.coord[0];
                const dy = city1.coord[1] - city2.coord[1];
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                // 如果距离太近，进行偏移调整
                if (distance < minDistance && distance > 0) {
                    const angle = Math.atan2(dy, dx);
                    const offsetX = Math.cos(angle) * offsetRange;
                    const offsetY = Math.sin(angle) * offsetRange;
                    
                    // 给第二个城市添加偏移
                    adjustedCities[j] = {
                        ...city2,
                        coord: [
                            city2.coord[0] - offsetX,
                            city2.coord[1] - offsetY
                        ]
                    };
                    
                    console.log(`调整节点位置: ${city1.name} 和 ${city2.name} 距离过近，给 ${city2.name} 添加偏移`);
                }
            }
        }
        
        return adjustedCities;
    };

    // 处理节点防重叠
    const adjustedCities = adjustNodePositions(cities);
    console.log('节点位置调整完成');

    // 更新连接线坐标以匹配调整后的节点位置
    const updateConnectionCoords = (connections, originalCities, adjustedCities) => {
        return connections.map(conn => {
            const updatedCoords = conn.coords.map(coord => {
                // 找到原始坐标对应的城市
                const originalCity = originalCities.find(city => 
                    Math.abs(city.coord[0] - coord[0]) < 0.01 && 
                    Math.abs(city.coord[1] - coord[1]) < 0.01
                );
                
                if (originalCity) {
                    // 找到调整后的对应城市
                    const adjustedCity = adjustedCities.find(city => city.name === originalCity.name);
                    if (adjustedCity) {
                        return adjustedCity.coord;
                    }
                }
                
                return coord; // 如果找不到对应城市，保持原坐标
            });
            
            return {
                ...conn,
                coords: updatedCoords
            };
        });
    };

    const adjustedConnections = updateConnectionCoords(processedConnections, cities, adjustedCities);
    console.log('连接线坐标已同步更新');

    const getNodeSize = (city) => {
        // 更大的统一尺寸
        return 30;
    };

    const getLineColor = (conn, index) => {
        // 统一使用绿色
        return '#00ff00';
    };

    const getLineWidth = (conn, index) => {
        // 统一线宽
        return 2;
    };

    const hasAnimation = (conn) => {
        // 不预设重要连接，统一无动画
        return false;
    };

    const getAnimationPeriod = (conn) => {
        // 统一动画周期（虽然现在不使用）
        return 6;
    };

    return {
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                if (params.seriesType === 'lines') {
                    const conn = processedConnections.find(c => c.name === params.data.name);
                    if (conn) {
                        // 获取友好的链路名称显示
                        let friendlyLinkName = conn.name;
                        
                        // 解析链路ID (格式: "BJ001-SH002" 或 "0-1")
                        const parts = conn.name.split('-');
                        if (parts.length === 2) {
                            const [sourceId, targetId] = parts;
                            
                            // 获取当前切片的拓扑数据
                            const currentTopology = networkTopology.value;
                            if (currentTopology && currentTopology.cities) {
                                // 查找对应的城市名称 - 支持字符串ID和数字ID
                                let sourceCity, targetCity;
                                
                                // 尝试按字符串ID查找
                                sourceCity = currentTopology.cities.find(city => city.id === sourceId);
                                targetCity = currentTopology.cities.find(city => city.id === targetId);
                                
                                // 如果没找到，尝试按数字ID查找
                                if (!sourceCity || !targetCity) {
                                    const sourceNumId = parseInt(sourceId);
                                    const targetNumId = parseInt(targetId);
                                    if (!isNaN(sourceNumId) && !isNaN(targetNumId)) {
                                        sourceCity = currentTopology.cities.find(city => city.id === sourceNumId);
                                        targetCity = currentTopology.cities.find(city => city.id === targetNumId);
                                    }
                                }
                                
                                if (sourceCity && targetCity) {
                                    friendlyLinkName = `${sourceCity.name} ↔ ${targetCity.name}`;
                                }
                            }
                        }
                        
                        return `
                            <div style="font-weight: bold;">${friendlyLinkName}</div>
                            <div>IP: ${conn.IP || 'N/A'}</div>
                            <div>IPv6: ${conn.IPv6 || 'N/A'}</div>
                        `;
                    }
                } else if (params.seriesType === 'scatter') {
                    return `<div style="font-weight: bold;">${params.data.name}</div>`;
                }
                return params.name;
            }
        },
        geo: {
            map: 'china',
            center: [104, 35],
            zoom: 1.5,
            roam: true,
            scaleLimit: {
                min: 0.3,
                max: 8
            },
            layoutCenter: ['50%', '50%'],
            layoutSize: '70%',
            itemStyle: {
                areaColor: '#e0f3ff',
                borderColor: '#b3d9ff',
                borderWidth: 1
            },
            emphasis: {
                itemStyle: {
                    areaColor: '#cce8ff'
                }
            }
        },
        series: [
            // 连接线 - 先绘制线条
            {
                name: '网络连接',
                type: 'lines',
                coordinateSystem: 'geo',
                data: adjustedConnections.map((conn, index) => ({
                    name: conn.name,
                    coords: conn.coords,
                    lineStyle: {
                        color: getLineColor(conn, index),
                        width: getLineWidth(conn, index),
                        type: 'solid'
                    },
                    effect: {
                        show: hasAnimation(conn),
                        period: getAnimationPeriod(conn),
                        trailLength: 0,
                        symbol: 'pin',
                        symbolSize: 3 // 统一动画符号大小
                    }
                })),
                emphasis: {
                    lineStyle: {
                        width: 6,
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            },
            // 城市节点 - 后绘制节点确保在最上层
            {
                name: '网络节点',
                type: 'scatter',
                coordinateSystem: 'geo',
                symbol: 'circle',
                symbolSize: 12, // 再小一半的节点大小
                itemStyle: {
                    color: '#000000', // 黑色节点
                    borderColor: '#ffffff',
                    borderWidth: 1,
                    shadowBlur: 2,
                    shadowColor: 'rgba(0, 0, 0, 0.2)'
                },
                data: adjustedCities.map((city, index) => {
                    console.log(`处理城市节点 ${index}: ${city.name}, 坐标: [${city.coord[0]}, ${city.coord[1]}]`);
                    return {
                        name: city.name,
                        coord: city.coord,
                        AS: city.AS,
                        id: city.id,
                        value: [city.coord[0], city.coord[1], city.name] // 确保ECharts能正确识别坐标
                    };
                }),
                label: {
                    show: true, // 显示标签
                    position: 'right',
                    formatter: '{b}',
                    fontSize: 14,
                    color: '#000',
                    fontWeight: 'bold'
                },
                emphasis: {
                    label: {
                        show: true, // 悬停时显示标签
                        fontSize: 16,
                        fontWeight: 'bold'
                    },
                    itemStyle: {
                        color: '#333333', // 悬停时稍微浅一点的黑色
                        borderColor: '#ffffff',
                        borderWidth: 4,
                        shadowBlur: 15,
                        shadowColor: 'rgba(0, 0, 0, 0.6)'
                    }
                }
            }
        ],
        toolbox: {
            feature: {
                restore: {
                    title: '还原'
                },
                saveAsImage: {
                    title: '保存为图片'
                }
            },
            right: 15,
            top: 15,
            iconStyle: {
                borderColor: '#999'
            },
            emphasis: {
                iconStyle: {
                    borderColor: '#666'
                }
            }
        }
    };
});

// 拓扑图配置（无地理坐标的网络拓扑图）
const topologyOptions = computed(() => {
    console.log('=== 拓扑图计算开始 ===');
    console.log('当前选择的切片:', selectedSlice.value);
    console.log('所有切片拓扑数据键名:', Object.keys(allSliceTopologies.value));
    console.log('所有切片信息:', selectedSliceInfo.value);
    console.log('切片加载状态:', isTopologyLoading.value);
    
    // 获取当前选择切片的拓扑数据
    const sliceInfo = selectedSliceInfo.value;
    let sliceKey = 'physical-network'; // 默认值
    let currentSliceTopology = null;
    
    if (sliceInfo && sliceInfo.filename) {
        sliceKey = sliceInfo.filename.replace('.json', '');
    }
    
    // 从allSliceTopologies中获取数据
    currentSliceTopology = allSliceTopologies.value[sliceKey];
    
    // 如果没有找到，尝试其他可能的键名
    if (!currentSliceTopology && Object.keys(allSliceTopologies.value).length > 0) {
        console.log('未找到切片数据，尝试其他键名');
        console.log('可用的键名:', Object.keys(allSliceTopologies.value));
        console.log('查找的键名:', sliceKey);
        
        // 尝试不带.json后缀的原始文件名
        if (sliceInfo && sliceInfo.filename) {
            const altKey = sliceInfo.filename;
            currentSliceTopology = allSliceTopologies.value[altKey];
            if (currentSliceTopology) {
                sliceKey = altKey;
                console.log('使用替代键名:', altKey);
            }
        }
        
        // 如果还是没找到，使用第一个可用的
        if (!currentSliceTopology) {
            const firstKey = Object.keys(allSliceTopologies.value)[0];
            currentSliceTopology = allSliceTopologies.value[firstKey];
            sliceKey = firstKey;
            console.log('使用第一个可用的切片:', firstKey);
        }
    }
    
    console.log('当前切片文件名:', sliceKey);
    console.log('当前切片拓扑数据:', currentSliceTopology);
    
    // 如果数据还在加载中
    if (isTopologyLoading.value) {
        return {
            title: {
                text: '正在加载切片数据...',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#1890ff',
                    fontSize: 16
                }
            }
        };
    }
    
    if (!currentSliceTopology) {
        console.log('当前切片拓扑数据不存在');
        return {
            title: {
                text: `切片拓扑数据不存在\n(${sliceKey})`,
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#999',
                    fontSize: 16
                }
            }
        };
    }

    // 检查是否为错误状态
    if (currentSliceTopology.error) {
        console.log('切片拓扑数据错误:', currentSliceTopology.message);
        return {
            title: {
                text: currentSliceTopology.message || '切片拓扑数据加载失败',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#f56c6c',
                    fontSize: 16
                }
            }
        };
    }

    // 检查数据结构 - 直接基于JSON数据处理
    let nodes = [];
    let connections = [];
    
    // 如果有cities和connections数据，直接转换
    if (currentSliceTopology.cities && Array.isArray(currentSliceTopology.cities) && 
        currentSliceTopology.connections && Array.isArray(currentSliceTopology.connections)) {
        
        console.log('处理cities和connections数据');
        const { cities, connections: sliceConnections } = currentSliceTopology;
        
        // 直接将cities转换为节点
        nodes = cities.map(city => ({
            id: city.name,
            name: city.name
        }));
        
        // 根据connections的points字段生成连接关系
        const allConnections = [];
        sliceConnections.forEach(conn => {
            const points = conn.points;
            
            // 如果只有两个点，直接连接
            if (points.length === 2) {
                const sourceCity = cities.find(c => c.id === points[0]);
                const targetCity = cities.find(c => c.id === points[1]);
                
                if (sourceCity && targetCity) {
                    allConnections.push({
                        source: sourceCity.name,
                        target: targetCity.name,
                        name: `${sourceCity.id}-${targetCity.id}` // 使用ID格式
                    });
                }
            }
            // 如果有多个点，两两相连
            else if (points.length > 2) {
                for (let i = 0; i < points.length; i++) {
                    for (let j = i + 1; j < points.length; j++) {
                        const point1 = points[i];
                        const point2 = points[j];
                        
                        const city1 = cities.find(c => c.id === point1);
                        const city2 = cities.find(c => c.id === point2);
                        
                        if (city1 && city2) {
                            allConnections.push({
                                source: city1.name,
                                target: city2.name,
                                name: `${city1.id}-${city2.id}` // 使用ID格式
                            });
                        }
                    }
                }
            }
        });
        
        connections = allConnections;
        console.log(`处理完成: ${nodes.length}个节点, ${connections.length}个连接`);
        
    } else if (currentSliceTopology.nodes && Array.isArray(currentSliceTopology.nodes)) {
        // 如果有直接的nodes数据
        nodes = currentSliceTopology.nodes;
        connections = currentSliceTopology.connections || currentSliceTopology.links || [];
    } else {
        console.log('数据结构不匹配，使用默认数据');
        // 简单的默认数据
        nodes = [
            { id: 'node1', name: '节点1' },
            { id: 'node2', name: '节点2' },
            { id: 'node3', name: '节点3' },
            { id: 'node4', name: '节点4' }
        ];
        connections = [
            { source: 'node1', target: 'node2', name: '1' },
            { source: 'node2', target: 'node3', name: '2' },
            { source: 'node3', target: 'node4', name: '3' },
            { source: 'node1', target: 'node4', name: '4' }
        ];
    }

    console.log('使用的节点数据:', nodes);
    console.log('使用的连接数据:', connections);

    if (!nodes || nodes.length === 0) {
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

    try {
        // 直接处理节点数据
        const processedNodes = nodes.map((node, index) => {
            return {
                id: node.id || node.name || `node_${index}`,
                name: node.name || node.id || `节点${index}`,
                symbolSize: 40,
                itemStyle: {
                    color: '#3498DB'
                },
                label: {
                    show: true,
                    color: '#2c3e50',
                    fontSize: 12
                }
            };
        });

        // 直接处理连接数据
        const processedLinks = connections.map((conn, index) => {
            return {
                source: conn.source || processedNodes[0]?.id,
                target: conn.target || processedNodes[1]?.id,
                name: conn.name || `${index}`,
                lineStyle: {
                    color: '#95A5A6',
                    width: 3,
                    opacity: 0.8
                },
                label: {
                    show: true,
                    position: 'middle',
                    fontSize: 10,
                    color: '#666'
                }
            };
        });

        console.log('处理后的节点总数:', processedNodes.length);
        console.log('处理后的连接总数:', processedLinks.length);
        console.log('所有节点ID:', processedNodes.map(n => n.id));
        console.log('所有连接源目标:', processedLinks.map(l => `${l.source} -> ${l.target}`));

        const config = {
            title: {
                text: `${selectedSliceInfo.value?.name || '网络'} - 拓扑图`,
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
                    try {
                        if (params.dataType === 'node') {
                            return `<strong>${params.data.name}</strong>`;
                        } else if (params.dataType === 'edge') {
                            return `${params.data.source} ↔ ${params.data.target}`;
                        }
                    } catch (e) {
                        console.error('Tooltip格式化错误:', e);
                    }
                    return '';
                }
            },
            legend: {
                data: [{
                    name: '节点',
                    icon: 'circle'
                }],
                right: 15,
                top: 15,
                orient: 'vertical'
            },
            series: [{
                name: '网络拓扑',
                type: 'graph',
                layout: 'force',
                data: processedNodes,
                links: processedLinks,
                roam: true,
                draggable: true,
                itemStyle: {
                    borderColor: '#fff',
                    borderWidth: 2,
                    shadowBlur: 6,
                    shadowColor: 'rgba(0, 0, 0, 0.2)'
                },
                lineStyle: {
                    opacity: 0.8,
                    curveness: 0.1
                },
                emphasis: {
                    focus: 'adjacency',
                    lineStyle: {
                        width: 4,
                        opacity: 1
                    },
                    itemStyle: {
                        shadowBlur: 15,
                        shadowColor: 'rgba(0, 0, 0, 0.4)'
                    }
                },
                force: {
                    repulsion: 2000,      // 增加节点间斥力，避免重叠
                    gravity: 0.1,         // 减小重力，给节点更多展开空间
                    edgeLength: [80, 200], // 增加边长范围，让连接更明显
                    layoutAnimation: true,
                    friction: 0.6         // 增加摩擦力，稳定布局
                }
            }]
        };

        console.log('最终拓扑图配置:', config);
        return config;

    } catch (error) {
        console.error('拓扑图生成错误:', error);
        return {
            title: {
                text: `拓扑图生成失败: ${error.message}`,
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#f56c6c',
                    fontSize: 16
                }
            }
        };
    }
});

// 链路可用性数据
const linkAvailability = ref({
    available: 31,
    unavailable: 0,
    unknown: 0,
    exception: 5,
    total: 36
});

// 全网可用性数据 - 根据当前问题动态计算
const networkAvailability = computed(() => {
    const activeSlices = sliceStats.value.active; // 总计 = 活跃切片数
    
    // 统计不同状态的切片
    let unavailable = 0; // 不可用 (高严重程度的未处理问题)
    let exception = 0;   // 异常 (中低严重程度的未处理问题)
    let unknown = 0;     // 未知 (处理中的问题)
    
    // 记录每个切片的状态，避免重复计算
    const sliceStatus = new Map();
    
    currentIssuesData.value.forEach(issue => {
        const sliceName = issue.slice;
        const severity = issue.severity;
        const status = issue.status;
        
        // 如果切片既有未处理又有处理中，优先算未处理
        if (status === "待处理" || status === "未处理") {
            if (severity === "高") {
                sliceStatus.set(sliceName, 'unavailable');
            } else if (severity === "中" || severity === "低") {
                // 只有在没有高优先级问题时才设置为异常
                if (!sliceStatus.has(sliceName) || sliceStatus.get(sliceName) !== 'unavailable') {
                    sliceStatus.set(sliceName, 'exception');
                }
            }
        } else if (status === "处理中") {
            // 只有在没有未处理问题时才设置为处理中
            if (!sliceStatus.has(sliceName)) {
                sliceStatus.set(sliceName, 'unknown');
            }
        }
    });
    
    // 统计各种状态的数量
    sliceStatus.forEach(status => {
        switch (status) {
            case 'unavailable':
                unavailable++;
                break;
            case 'exception':
                exception++;
                break;
            case 'unknown':
                unknown++;
                break;
        }
    });
    
    // 可用切片 = 总切片数 - 有问题的切片数
    const available = activeSlices - unavailable - exception - unknown;
    
    return {
        available: Math.max(0, available),
        unavailable,
        unknown,
        exception,
        total: activeSlices
    };
});


const routeData = computed(() => {
    if (!networkTopology.value) return {};
    
    const routes = {};
    networkTopology.value.connections.forEach((conn, index) => {
        routes[conn.name] = {
            dates: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:59'],
            orders: generateRandomDelayData(),
            color: '#00ff00' // 使用绿色，与地图线条颜色一致
        };
    });
    
    return routes;
});

// 生成随机延迟数据
const generateRandomDelayData = () => {
    return Array.from({ length: 7 }, () => Math.floor(Math.random() * 50) + 10);
};

// 时间线图表配置
// 时间线图表配置 - 使用真实时延数据
const timelineOptions = computed(() => {
    // 如果正在加载数据
    if (delayDataLoading.value) {
        return {
            title: {
                text: '加载时延数据中...',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#1890ff',
                    fontSize: 14
                }
            },
            grid: { show: false },
            xAxis: { show: false },
            yAxis: { show: false },
            series: []
        };
    }

    // 如果有错误
    if (delayDataError.value) {
        let errorTitle = '数据加载失败';
        let errorSubtitle = delayDataError.value;
        
        if (delayDataError.value.includes('数据库服务未启动')) {
            errorTitle = '数据库服务未启动';
            errorSubtitle = '请在终端运行:\ncd database && node db-service.js';
        }
        
        return {
            title: {
                text: errorTitle,
                left: 'center',
                top: 'center',
                textStyle: {
                    color: '#f56c6c',
                    fontSize: 16,
                    fontWeight: 'bold'
                }
            },
            subtitle: {
                text: errorSubtitle,
                left: 'center',
                top: '60%',
                textStyle: {
                    color: '#666',
                    fontSize: 12,
                    lineHeight: 20
                }
            },
            grid: { show: false },
            xAxis: { show: false },
            yAxis: { show: false },
            series: []
        };
    }

    // 如果没有数据
    if (!realDelayData.value || !Array.isArray(realDelayData.value) || realDelayData.value.length === 0) {
        return {
            title: {
                text: '暂无时延数据\n请确保数据库服务已启动',
                left: 'center',
                top: 'middle',
                textStyle: {
                    color: '#999',
                    fontSize: 14
                }
            },
            grid: { show: false },
            xAxis: { show: false },
            yAxis: { show: false },
            series: []
        };
    }

    // 处理真实时延数据
    let filteredData = realDelayData.value;
    
    // 根据选中的切片过滤数据
    if (selectedSlice.value && selectedSlice.value !== 'all') {
        // 直接使用切片名称，不需要映射
        filteredData = filteredData.filter(item => item.slice === selectedSlice.value);
        console.log(`过滤切片: ${selectedSlice.value}`);
        console.log(`切片过滤后数据量: ${filteredData.length}`);
    }
    
    // 根据选中的链路过滤数据
    if (selectedRoute.value && selectedRoute.value !== 'all') {
        const [src, dst] = selectedRoute.value.split('-');
        console.log(`选中链路: ${selectedRoute.value}, 源: ${src}, 目标: ${dst}`);
        if (src && dst) {
            // 支持双向连接过滤：既匹配 src->dst 也匹配 dst->src
            filteredData = filteredData.filter(item => 
                (item.src === src && item.dst === dst) || 
                (item.src === dst && item.dst === src)
            );
            console.log(`链路过滤后数据量: ${filteredData.length}`);
            console.log(`样本数据:`, filteredData.slice(0, 3));
        }
    }
    
    console.log(`最终过滤后数据量: ${filteredData.length}`);
    console.log(`样本数据:`, filteredData.slice(0, 3));
    
    // 验证过滤结果
    if (filteredData.length === 0) {
        console.warn('过滤后没有数据，检查过滤条件:');
        console.warn(`- 切片: ${selectedSlice.value}`);
        console.warn(`- 链路: ${selectedRoute.value}`);
        console.warn(`- 原始数据量: ${realDelayData.value ? realDelayData.value.length : 0}`);
    }
    
    const timeGroups = {};
    filteredData.forEach(item => {
        if (item && item.timestamp && item.delay !== null && item.delay !== undefined) {
            const hour = new Date(item.timestamp).getHours();
            if (!timeGroups[hour]) {
                timeGroups[hour] = [];
            }
            // 确保delay是数字类型，API返回的可能是字符串
            const delayValue = typeof item.delay === 'string' ? parseFloat(item.delay) : item.delay;
            if (!isNaN(delayValue)) {
                timeGroups[hour].push(delayValue);
            }
        }
    });

    // 计算每小时平均时延
    const hours = [];
    const avgDelays = [];
    for (let i = 0; i < 24; i++) {
        hours.push(`${i.toString().padStart(2, '0')}:00`);
        if (timeGroups[i] && timeGroups[i].length > 0) {
            const avg = timeGroups[i].reduce((sum, delay) => sum + delay, 0) / timeGroups[i].length;
            avgDelays.push(Math.round(avg * 100) / 100);
        } else {
            avgDelays.push(0);
        }
    }

    return {
        title: {
            text: (() => {
                let title = '24小时链路时延趋势';
                if (selectedSlice.value && selectedSlice.value !== 'all') {
                    title += ` - ${selectedSlice.value}切片`;
                }
                if (selectedRoute.value && selectedRoute.value !== 'all') {
                    // 直接在这里处理链路名称转换
                    let linkDisplayName = selectedRoute.value;
                    
                    // 解析链路ID (格式: "BJ001-SH002" 或 "0-1")
                    const parts = selectedRoute.value.split('-');
                    if (parts.length === 2) {
                        const [sourceId, targetId] = parts;
                        
                        // 获取当前切片的拓扑数据
                        const currentTopology = networkTopology.value;
                        if (currentTopology && currentTopology.cities) {
                            // 查找对应的城市名称 - 支持字符串ID和数字ID
                            let sourceCity, targetCity;
                            
                            // 尝试按字符串ID查找
                            sourceCity = currentTopology.cities.find(city => city.id === sourceId);
                            targetCity = currentTopology.cities.find(city => city.id === targetId);
                            
                            // 如果没找到，尝试按数字ID查找
                            if (!sourceCity || !targetCity) {
                                const sourceNumId = parseInt(sourceId);
                                const targetNumId = parseInt(targetId);
                                if (!isNaN(sourceNumId) && !isNaN(targetNumId)) {
                                    sourceCity = currentTopology.cities.find(city => city.id === sourceNumId);
                                    targetCity = currentTopology.cities.find(city => city.id === targetNumId);
                                }
                            }
                            
                            if (sourceCity && targetCity) {
                                linkDisplayName = `${sourceCity.name} ↔ ${targetCity.name}`;
                            }
                        }
                    }
                    
                    title += ` - ${linkDisplayName}`;
                }
                return title;
            })(),
            left: 'center',
            top: '5%',
            textStyle: {
                fontSize: 14,
                color: '#333',
                fontWeight: 'normal'
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                let tooltipContent = `时间: ${params[0].axisValue}<br/>平均时延: ${params[0].value}ms`;
                
                // 添加当前选择信息
                if (selectedSlice.value && selectedSlice.value !== 'all') {
                    tooltipContent += `<br/>切片: ${selectedSlice.value}`;
                }
                if (selectedRoute.value && selectedRoute.value !== 'all') {
                    // 直接在这里处理链路名称转换
                    let linkDisplayName = selectedRoute.value;
                    
                    // 解析链路ID (格式: "BJ001-SH002" 或 "0-1")
                    const parts = selectedRoute.value.split('-');
                    if (parts.length === 2) {
                        const [sourceId, targetId] = parts;
                        
                        // 获取当前切片的拓扑数据
                        const currentTopology = networkTopology.value;
                        if (currentTopology && currentTopology.cities) {
                            // 查找对应的城市名称 - 支持字符串ID和数字ID
                            let sourceCity, targetCity;
                            
                            // 尝试按字符串ID查找
                            sourceCity = currentTopology.cities.find(city => city.id === sourceId);
                            targetCity = currentTopology.cities.find(city => city.id === targetId);
                            
                            // 如果没找到，尝试按数字ID查找
                            if (!sourceCity || !targetCity) {
                                const sourceNumId = parseInt(sourceId);
                                const targetNumId = parseInt(targetId);
                                if (!isNaN(sourceNumId) && !isNaN(targetNumId)) {
                                    sourceCity = currentTopology.cities.find(city => city.id === sourceNumId);
                                    targetCity = currentTopology.cities.find(city => city.id === targetNumId);
                                }
                            }
                            
                            if (sourceCity && targetCity) {
                                linkDisplayName = `${sourceCity.name} ↔ ${targetCity.name}`;
                            }
                        }
                    }
                    
                    tooltipContent += `<br/>链路: ${linkDisplayName}`;
                }
                
                return tooltipContent;
            }
        },
        grid: {
            left: '8%',
            right: '8%',
            bottom: '15%',
            top: '20%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: hours,
            axisLine: {
                lineStyle: { color: '#ddd' }
            },
            axisLabel: {
                color: '#666',
                fontSize: 10
            },
            name: '时间',
            nameLocation: 'middle',
            nameGap: 25,
            nameTextStyle: {
                color: '#666',
                fontSize: 12
            }
        },
        yAxis: {
            type: 'value',
            name: '时延(ms)',
            axisLine: {
                lineStyle: { color: '#ddd' }
            },
            axisLabel: {
                color: '#666',
                fontSize: 10
            },
            splitLine: {
                lineStyle: { color: '#f0f0f0' }
            }
        },
        series: [
            {
                name: '平均时延',
                type: 'line',
                data: avgDelays,
                smooth: true,
                symbol: 'circle',
                symbolSize: 4,
                lineStyle: {
                    color: '#5470c6',
                    width: 2
                },
                itemStyle: {
                    color: '#5470c6'
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [{
                            offset: 0, color: 'rgba(84, 112, 198, 0.3)'
                        }, {
                            offset: 1, color: 'rgba(84, 112, 198, 0.1)'
                        }]
                    }
                }
            }
        ]
    };
});

// 地图和拓扑图点击事件处理
const handleMapClick = (params: any) => {
    console.log('图表点击事件:', params);
    
    // 处理地理视图的连接线点击事件
    if (params.seriesType === 'lines' && params.data && params.data.name) {
        selectedRoute.value = params.data.name;
        console.log(`地理视图选中链路: ${selectedRoute.value}`);
    }
    
    // 处理拓扑视图的边点击事件
    else if (params.seriesType === 'graph' && params.dataType === 'edge' && params.data) {
        // 拓扑图的边点击
        if (params.data.name) {
            selectedRoute.value = params.data.name;
            console.log(`拓扑视图选中链路: ${selectedRoute.value}`);
        } else if (params.data.source && params.data.target) {
            // 如果没有name字段，从source和target构建链路名称
            selectedRoute.value = `${params.data.source}-${params.data.target}`;
            console.log(`拓扑视图构建链路名称: ${selectedRoute.value}`);
        }
    }
    
    // 处理拓扑视图的节点点击事件（可选功能）
    else if (params.seriesType === 'graph' && params.dataType === 'node' && params.data) {
        console.log(`拓扑视图点击节点: ${params.data.name}`);
        // 可以在这里添加节点点击的处理逻辑
    }
};

// 当前问题数据 - 从加载的警报数据获取
const currentIssuesData = computed(() => {
    return alertData.value?.currentIssues || [];
});

// 选择的切片组
const selectedSliceGroup = ref(1);

// 切片组配置
const sliceGroups = computed(() => {
    const activeSliceCount = networkSlices.value.length;
    const groups = [];
    const totalGroups = Math.ceil(activeSliceCount / 10);
    
    for (let i = 1; i <= totalGroups; i++) {
        const start = (i - 1) * 10 + 1;
        const end = Math.min(i * 10, activeSliceCount);
        groups.push({
            value: i,
            label: `${start}-${end}`
        });
    }
    
    return groups;
});

// 总切片数配置
const totalSlicesCount = ref(4096);

// 切片统计数据
const sliceStats = computed(() => {
    const total = totalSlicesCount.value; // 从配置中读取总切片数
    const active = networkSlices.value.length; // 活跃切片数 = 实际切片数量
    const warning = total - active; // 空闲切片数 = 总数 - 活跃数

    return {
        total,
        active,
        warning
    };
});

// 当前显示的切片数据（基于选择的组）
const displayedSlices = computed(() => {
    const startIndex = (selectedSliceGroup.value - 1) * 10;
    const endIndex = selectedSliceGroup.value * 10;
    return networkSlices.value.slice(startIndex, endIndex);
});

// 过滤后的切片数据（使用动态加载的切片数据）
const filteredSliceData = computed(() => {
    return networkSlices.value;
});

// 切片组变化处理
const handleSliceGroupChange = (value: number) => {
    selectedSliceGroup.value = value;
    
    // 检查当前选择的切片是否在新组中，如果不在则重置选择
    const currentSelectedInNewGroup = displayedSlices.value.find(slice => slice.id === selectedSlice.value);
    if (!currentSelectedInNewGroup && displayedSlices.value.length > 0) {
        // 如果当前选择的切片不在新组中，选择新组的第一个切片
        selectSlice(displayedSlices.value[0].id);
    }
};

// 问题类型颜色映射
const getIssueTypeColor = (type: string) => {
    if (alertData.value?.alertTypes?.[type]) {
        return alertData.value.alertTypes[type].color;
    }
    // 默认映射
    const colorMap: { [key: string]: string } = {
        '延迟下降': 'warning',
        '中断': 'danger',
        '连接异常': 'danger',
        '性能下降': 'warning',
        '带宽不足': 'warning',
        '设备故障': 'danger',
        '安全告警': 'info',
        '配置错误': 'warning',
        '网络拥塞': 'warning',
        '硬件故障': 'danger',
        '软件异常': 'warning',
        '温度告警': 'info'
    };
    return colorMap[type] || '';
};

// 严重程度颜色映射
const getSeverityColor = (severity: string) => {
    if (alertData.value?.severityMapping?.[severity]) {
        return alertData.value.severityMapping[severity];
    }
    // 默认映射
    const colorMap: { [key: string]: string } = {
        '高': 'danger',
        '中': 'warning',
        '低': 'info'
    };
    return colorMap[severity] || '';
};

// 状态颜色映射
const getStatusColor = (status: string) => {
    if (alertData.value?.statusMapping?.[status]) {
        return alertData.value.statusMapping[status];
    }
    // 默认映射
    const colorMap: { [key: string]: string } = {
        '处理中': 'warning',
        '已确认': 'info',
        '待处理': 'danger',
        '已解决': 'success',
        '监控中': 'info'
    };
    return colorMap[status] || '';
};

// 切片类型颜色映射
const getSliceTypeColor = (type: string) => {
    const colorMap: { [key: string]: string } = {
        'Physical': 'info',
        'eMBB': 'success',
        'URLLC': 'warning',
        'mMTC': 'info'
    };
    return colorMap[type] || '';
};

// 根据切片名称获取切片类型
const getSliceTypeByName = (sliceName: string) => {
    if (sliceName.includes('物理网')) return 'Physical';
    if (sliceName.includes('eMBB')) return 'eMBB';
    if (sliceName.includes('URLLC')) return 'URLLC';
    if (sliceName.includes('mMTC') || sliceName.includes('IoT')) return 'mMTC';
    return 'Physical'; // 默认类型
};

// 切片状态颜色映射
const getSliceStatusColor = (status: string) => {
    const colorMap: { [key: string]: string } = {
        '正常': 'success',
        '告警': 'danger',
        '维护': 'warning'
    };
    return colorMap[status] || '';
};

// 使用率颜色映射
const getUsageColor = (usage: number) => {
    if (usage >= 90) return '#ff4d4f';
    if (usage >= 70) return '#faad14';
    return '#52c41a';
};

// 组件挂载时加载网络拓扑数据和警报数据
// 监听切片和链路选择变化，重新加载数据
watch([selectedSlice, selectedRoute], ([newSlice, newRoute]) => {
    console.log('切片或链路选择变化:', { slice: newSlice, route: newRoute });
    // 不需要重新调用 loadDelayData，因为 timelineOptions 会自动根据选择过滤数据
}, { immediate: false });

onMounted(async () => {
    await loadNetworkTopology();
    loadAlertData();
    loadDelayData(); // 加载实时时延数据
    // 初始化默认切片（物理网络）的拓扑和探测数据
    switchSliceTopology('physical-network');
    
    // 确保初始选择第一组的第一个切片
    if (displayedSlices.value.length > 0) {
        selectSlice(displayedSlices.value[0].id);
    }
});
</script>

<style>
/* 全局样式重置 - 消除默认留白 */
* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow-x: hidden;
}

.card-body {
    display: flex;
    align-items: center;
    height: 100px;
    padding: 0;
}
</style>
<style scoped>
/* 通用间距类 */
.mgb20 {
    margin-bottom: 20px !important;
}

.mgb15 {
    margin-bottom: 15px !important;
}

.mgb10 {
    margin-bottom: 10px !important;
}

/* 响应式行间距 */
.responsive-row {
    margin-bottom: 20px;
}

.responsive-row:last-child {
    margin-bottom: 0; /* 最后一行底部不留间距 */
}

/* 卡片间距 */
.responsive-card {
    margin-bottom: 15px;
    height: auto;
    min-height: 300px; /* 恢复基础高度 */
}

/* 确保页面底部有足够间距 */
.dashboard-container {
    padding-bottom: 0; /* 移除页面底部间距 */
    min-height: 100vh; /* 确保容器至少填满整个视口高度 */
    display: flex;
    flex-direction: column;
}

.card-content {
    flex: 1;
    text-align: center;
    font-size: 14px;
    color: #999;
    padding: 0 20px;
}

.card-num {
    font-size: 30px;
}

.card-icon {
    font-size: 50px;
    width: 100px;
    height: 100px;
    text-align: center;
    line-height: 100px;
    color: #fff;
}

.bg1 {
    background: #2d8cf0;
}

.bg2 {
    background: #64d572;
}

.bg3 {
    background: #f25e43;
}

.bg4 {
    background: #e9a745;
}

.color1 {
    color: #2d8cf0;
}

.color2 {
    color: #64d572;
}

.color3 {
    color: #f25e43;
}

.color4 {
    color: #e9a745;
}

.chart {
    width: 100%;
    height: 400px;
}

.card-header {
    padding: 8px 15px; /* 减少内边距 */
    margin-bottom: 15px; /* 减少底部间距 */
    border-bottom: 1px solid #f0f0f0; /* 添加分隔线 */
}

.card-header-title {
    font-size: 16px; /* 稍微减小字体 */
    font-weight: bold;
    margin-bottom: 5px; /* 减少标题和描述之间的间距 */
}

.card-header-desc {
    font-size: 13px; /* 减小描述文字 */
    color: #999;
    margin-bottom: 0;
}

.timeline-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 16px;
    color: #000;
}

.timeline-time,
.timeline-desc {
    font-size: 12px;
    color: #787878;
}

/* 图表容器布局 */
.chart-container {
    display: flex !important;
    flex-direction: row !important; /* 强制水平排列 */
    width: 100%;
    height: 100%;
    gap: 2px; /* 进一步减少左右组件之间的间距 */
    flex: 1;
    align-items: stretch; /* 确保子元素等高 */
    flex-wrap: nowrap !important; /* 禁止换行 */
    justify-content: flex-start; /* 改为左对齐，确保有足够间距 */
    padding: 0; /* 完全移除容器内边距 */
}

.left-component {
    flex: 0 0 24%; /* 增加左侧宽度到24% */
    display: flex;
    flex-direction: column;
    width: 24%; /* 增加左侧宽度到24% */
    max-width: 24%; /* 防止宽度超出 */
}

.right-component {
    flex: 0 0 76%; /* 增加右侧宽度到76% */
    display: flex;
    flex-direction: row; /* 地图和按钮水平排列 */
    width: 76%; /* 增加右侧宽度到76% */
    max-width: 76%; /* 防止宽度超出 */
    height: 100%;
    gap: 2px; /* 减少地图和按钮间的间距 */
}

/* 地图图表占据主要空间 */
.map-chart {
    flex: 1;
    height: 100%;
}

/* 地图/拓扑切换按钮样式 - 紧贴右边框 */
.view-mode-switcher {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 8px;
    padding: 20px 0px 20px 5px; /* 右边距改为0，完全贴边 */
    background: transparent;
    border: none;
    width: auto;
    min-width: 0;
    flex-shrink: 0;
}

.switcher-buttons {
    display: flex;
    flex-direction: row;
    gap: 8px;
    align-items: center;
}

.view-mode-switcher .switcher-btn {
    font-size: 12px;
    padding: 6px 12px;
    width: auto;
    height: 32px;
    border-radius: 4px;
    border: none;
    background: rgba(255, 255, 255, 0.9);
    color: #606266;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    writing-mode: horizontal-tb;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    white-space: nowrap;
}

.view-mode-switcher .switcher-btn:hover {
    color: #409eff;
    background: rgba(64, 158, 255, 0.1);
    box-shadow: 0 2px 6px rgba(64, 158, 255, 0.2);
}

.view-mode-switcher .switcher-btn.is-active,
.view-mode-switcher .el-button--primary {
    background: #409eff;
    color: #ffffff;
    box-shadow: 0 2px 6px rgba(64, 158, 255, 0.4);
}

.switcher-description {
    margin-top: 5px;
    padding: 0 4px;
}

.description-text {
    font-size: 11px;
    color: #999999;
    line-height: 1.2;
    display: block;
    text-align: left;
    max-width: 120px;
}

/* 3D切片可视化样式 */
.slice-visualizer {
    width: 100%;
    height: 100%;
    border: 2px solid #e8e8e8;
    border-radius: 8px;
    background: linear-gradient(135deg, #f0f2f5 0%, #fafafa 100%);
    display: flex;
    flex-direction: column;
    min-height: 400px; /* 大幅增加切片可视化高度 */
    max-height: 450px; /* 增加最大高度 */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 12px; /* 进一步减少内边距 */
    overflow: hidden;
    position: relative;
}

.slice-header {
    text-align: center;
    margin-bottom: 15px; /* 减少底部间距 */
}

.slice-header h3 {
    margin: 0 0 5px 0; /* 减少间距 */
    font-size: 16px; /* 稍微减小字体 */
    color: #333;
    font-weight: 600;
}

.slice-header p {
    margin: 0;
    font-size: 12px; /* 减小描述文字 */
    color: #666;
}

.slice-stack-container {
    flex: 1;
    display: flex;
    align-items: flex-start; /* 从center改为flex-start，让内容靠上对齐 */
    justify-content: flex-start;
    perspective: 1500px;
    perspective-origin: center center;
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    padding-left: 20px; /* 减少左侧内边距 */
    padding-top: 100px; /* 进一步增加顶部内边距，让可视化区域更往下移 */
}

.zoom-controls {
    position: absolute;
    top: 20px;
    right: 20px;
    display: flex;
    gap: 5px;
    z-index: 100;
    background: rgba(255, 255, 255, 0.1);
    padding: 5px;
    border-radius: 6px;
    backdrop-filter: blur(10px);
}

.zoom-btn {
    width: 30px;
    height: 30px;
    border: 1px solid #ddd;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: bold;
    color: #666;
    transition: all 0.2s ease;
    backdrop-filter: blur(5px);
}

.zoom-btn:hover {
    background: rgba(24, 144, 255, 0.1);
    border-color: #1890ff;
    color: #1890ff;
}

.slice-stack {
    position: relative;
    width: 70%; /* 从50%增加到70% */
    height: 90%; /* 从85%增加到90% */
    transform-style: preserve-3d;
    transform: rotateX(15deg) rotateY(-10deg);
    transition: transform 0.3s ease;
}

.slice-layer {
    position: absolute;
    width: 100%;
    height: 120px; /* 从100px增加到120px */
    border: 3px solid #1890ff;
    border-radius: 12px;
    background: rgba(24, 144, 255, 0.1);
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(5px);
}

.slice-layer:hover {
    transform: translateZ(15px) translateY(-8px) scale(1.05);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.25);
    border-width: 4px;
}

.slice-layer.active {
    border-color: #ff4d4f;
    background: rgba(255, 77, 79, 0.15);
    box-shadow: 0 8px 16px rgba(255, 77, 79, 0.3);
    transform: translateZ(20px) translateY(-12px) scale(1.08);
}

.slice-content {
    text-align: center;
    color: #333;
    position: relative;
    z-index: 2;
    width: 100%;
}

.slice-name {
    font-size: 20px;
    font-weight: 700;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    padding: 0 20px;
}

.slice-tooltip {
    position: absolute;
    top: 50%;
    left: calc(100% + 15px);
    transform: translateY(-50%);
    background: rgba(0, 0, 0, 0.9);
    color: white;
    padding: 10px 15px;
    border-radius: 8px;
    font-size: 15px;
    z-index: 1000;
    white-space: nowrap;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    animation: fadeInRight 0.3s ease;
    pointer-events: none;
    backdrop-filter: blur(10px);
}

.slice-tooltip::after {
    content: '';
    position: absolute;
    top: 50%;
    left: -6px;
    transform: translateY(-50%);
    border: 6px solid transparent;
    border-right-color: rgba(0, 0, 0, 0.9);
}

.tooltip-title {
    font-weight: 600;
    margin: 0;
    color: #fff;
    font-size: 15px;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.tooltip-info {
    display: none !important;
}

.tooltip-info > div {
    display: none !important;
}

.selected-slice-info {
    margin-top: 8px; /* 进一步减少顶部间距，拉近与可视化区域的距离 */
    padding: 10px; /* 减少内边距 */
    background: rgba(255, 255, 255, 0.95); /* 稍微增加透明度 */
    border-radius: 6px; /* 稍微减小圆角 */
    border: 1px solid #e8e8e8;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); /* 减小阴影 */
}

.selected-slice-info h4 {
    margin: 0 0 8px 0; /* 减少底部间距 */
    font-size: 14px; /* 减小字体 */
    color: #333;
    font-weight: 600;
}

.slice-details {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.detail-item {
    padding: 4px 8px;
    background: #f0f2f5;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    color: #666;
}

.detail-item.正常 {
    background: #f6ffed;
    color: #52c41a;
    border: 1px solid #b7eb8f;
}

.detail-item.告警 {
    background: #fff2e8;
    color: #fa8c16;
    border: 1px solid #ffd591;
}

.detail-item.异常 {
    background: #fff1f0;
    color: #ff4d4f;
    border: 1px solid #ffb3b3;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateX(-50%) translateY(15px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateX(-50%) translateY(0) scale(1);
    }
}

@keyframes fadeInRight {
    from {
        opacity: 0;
        transform: translateY(-50%) translateX(-10px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateY(-50%) translateX(0) scale(1);
    }
}

.map-chart {
    width: 90%;
    flex: 1;
    min-height: 400px; /* 大幅增加地图组件高度 */
    max-height: 450px; /* 增加最大高度 */
    border: 2px solid #000000; /* 黑色边框 */
    border-radius: 8px; /* 圆角边框 */
    padding: 8px; /* 减少内边距 */
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 黑色阴影效果 */
    box-sizing: border-box; /* 确保边框包含在尺寸内 */
    background-color: #fafafa; /* 添加背景色，使边框更明显 */
}
.timeline-chart {
    width: 100%;
    flex: 1;
    min-height: 450px; /* 大幅增加时间线图表高度 */
    max-height: 500px; /* 增加最大高度 */
}

/* 链路可用性样式 */
.availability-container {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    height: auto;
    padding: 6px 4px;
    gap: 3px;
    min-height: 80px;
    flex-wrap: nowrap !important;
    flex-direction: row !important;
}

.availability-item {
    text-align: center;
    padding: 8px 4px;
    border-radius: 6px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    margin: 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.availability-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.availability-item.available {
    background: linear-gradient(135deg, #52c41a, #73d13d);
    color: white;
}

.availability-item.unavailable {
    background: linear-gradient(135deg, #ff4d4f, #ff7875);
    color: white;
}

.availability-item.unknown {
    background: linear-gradient(135deg, #8c8c8c, #bfbfbf);
    color: white;
}

.availability-item.exception {
    background: linear-gradient(135deg, #ff8c00, #ffa500);
    color: white;
}

.availability-item.total {
    background: linear-gradient(135deg, #1890ff, #40a9ff);
    color: white;
}

.availability-number {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 4px;
    line-height: 1;
}

.availability-label {
    font-size: 9px;
    opacity: 0.9;
    font-weight: 500;
}

/* 全网可用性样式 */
.network-availability {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 120px;
    padding: 10px;
}

.network-status-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.network-status-circle.excellent {
    background: linear-gradient(135deg, #52c41a, #73d13d);
    color: white;
}

.network-status-circle.good {
    background: linear-gradient(135deg, #1890ff, #40a9ff);
    color: white;
}

.network-status-circle.warning {
    background: linear-gradient(135deg, #faad14, #ffc53d);
    color: white;
}

.network-status-circle.danger {
    background: linear-gradient(135deg, #ff4d4f, #ff7875);
    color: white;
}

.network-percentage {
    font-size: 18px;
    font-weight: bold;
}

.network-status-text {
    font-size: 10px;
    opacity: 0.9;
}

.network-details {
    display: flex;
    gap: 15px;
    font-size: 12px;
}

.detail-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.detail-label {
    color: #666;
    margin-bottom: 2px;
}

.detail-value {
    font-weight: bold;
    color: #333;
}

/* 切片筛选条样式 */
.slice-filter-bar {
    background: #ffffff;
    border-radius: 8px;
    padding: 15px 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #e8e8e8;
}

.filter-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stats-section {
    display: flex;
    gap: 80px; /* 两组之间的距离增加一点点 */
    align-items: center;
}

/* 切片统计组 */
.slice-stats-group {
    display: flex;
    gap: 30px;
}

/* 可用性统计组 - 包含标题和色块 */
.availability-stats-group {
    display: flex;
    align-items: center;
    gap: 20px; /* 标题与色块之间的间距增加一点 */
}

/* 可用性标题 */
.availability-title {
    font-size: 14px;
    font-weight: 500;
    color: #333;
    white-space: nowrap;
}

/* 可用性色块容器 */
.availability-items {
    display: flex;
    gap: 2px; /* 色块之间很小的间距 */
}

/* 统计栏中的availability-item样式 */
.stats-section .availability-item {
    text-align: center;
    padding: 8px 12px;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    min-width: 60px;
}

.stats-section .availability-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.stats-section .availability-item.available {
    background: linear-gradient(135deg, #52c41a, #73d13d);
    color: white;
}

.stats-section .availability-item.unavailable {
    background: linear-gradient(135deg, #ff4d4f, #ff7875);
    color: white;
}

.stats-section .availability-item.unknown {
    background: linear-gradient(135deg, #8c8c8c, #bfbfbf);
    color: white;
}

.stats-section .availability-item.exception {
    background: linear-gradient(135deg, #ff8c00, #ffa500);
    color: white;
}

.stats-section .availability-item.total {
    background: linear-gradient(135deg, #1890ff, #40a9ff);
    color: white;
}

.stats-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.stats-number {
    font-size: 24px;
    font-weight: bold;
    color: #1890ff;
    margin-bottom: 4px;
}

.stats-number.active {
    color: #52c41a;
}

.stats-number.warning {
    color: #ff4d4f;
}

.stats-number.available {
    color: #52c41a;
}

.stats-number.exception {
    color: #faad14;
}

.stats-number.unavailable {
    color: #ff4d4f;
}

.stats-label {
    font-size: 12px;
    color: #666;
    font-weight: 500;
}

.filter-section {
    display: flex;
    align-items: center;
}

.filter-select {
    width: 150px;
    margin-left: 10px;
}

.filter-label {
    font-size: 14px;
    color: #333;
    font-weight: 500;
}

/* 响应式布局样式 */
.responsive-row {
    margin-bottom: 20px;
}

/* 可用性行 - 压缩30%高度 */
.availability-row {
    height: 176px;
    max-height: 176px;
    overflow: hidden;
    margin-bottom: 25px;
}

.availability-row .el-col {
    height: 100%;
}

.availability-row .responsive-card {
    height: 100% !important;
    min-height: unset !important;
}

.availability-row .el-card__body {
    height: calc(100% - 10px) !important;
    min-height: unset !important;
    padding: 10px !important;
}

.availability-row .card-header {
    margin-bottom: 10px;
}

/* 表格行 - 确保等高并紧挨着，水平排列 */
.table-row {
    margin-bottom: 0; /* 移除表格行底部间距 */
    display: flex !important;
    align-items: stretch;
    gap: 5px;
    flex-wrap: nowrap;
    min-height: 480px;
    height: 480px;
}

.table-row .el-col {
    display: flex !important;
    padding: 0 !important;
    flex: 1;
    height: 100%;
}

.table-row .el-col .table-card {
    width: 100%;
    height: 100%;
}

/* 主要卡片样式 */
.responsive-card .el-card__body {
    height: auto;
    min-height: 500px; /* 恢复卡片高度 */
    padding: 20px;
    display: flex !important;
    flex-direction: column !important;
    overflow: auto; /* 改为auto以允许滚动查看隐藏内容 */
}

/* 确保chart-container充分利用空间 */
.responsive-card .chart-container {
    flex: 1;
    min-height: 220px; /* 进一步降低内部组件高度 */
    max-height: 260px; /* 进一步降低最大高度 */
    display: flex !important;
    flex-direction: row !important; /* 确保水平布局 */
    overflow: hidden; /* 防止内容溢出 */
}

/* 可用性卡片 */
.availability-card .el-card__body {
    height: auto;
    display: flex;
    flex-direction: column;
}

/* 表格卡片 - 确保等高并添加滚动 */
.table-card {
    height: 100% !important;
    display: flex;
    flex-direction: column;
}

.table-card .el-card__body {
    display: flex;
    flex-direction: column;
    height: 100% !important;
    flex: 1;
    padding: 15px 15px 10px 15px; /* 恢复合适的内边距 */
    overflow: hidden;
}

/* 图表行样式 - 确保切片延迟和链路时延卡片等高 */
.chart-row {
    display: flex;
    align-items: stretch; /* 确保子元素等高 */
}

.chart-row .el-col {
    display: flex;
    flex-direction: column;
}

.chart-card {
    height: 100% !important;
    min-height: 600px; /* 增加最外层卡片容器的最小高度 */
    display: flex;
    flex-direction: column;
}

.chart-card .el-card__body {
    height: 100% !important;
    flex: 1;
    display: flex !important;
    flex-direction: column !important;
    padding: 20px;
    min-height: 550px; /* 从500px增加到550px，让卡片更高 */
    overflow: auto; /* 改为auto以允许滚动查看隐藏内容 */
}

/* 地图和切片可视化卡片特殊样式 */
.map-slice-card {
    min-height: 600px; /* 与chart-card保持一致的外层容器高度 */
}

.map-slice-card .el-card__body {
    min-height: 550px; /* 与chart-card保持一致的内部高度 */
    padding: 20px 0 20px 20px; /* 只移除右边距，保持其他方向的padding */
}

/* 确保chart-container和timeline-chart都充分利用空间 */
.chart-card .chart-container,
.chart-card .timeline-chart {
    flex: 1;
    min-height: 450px; /* 大幅增加内部组件高度 */
    max-height: 500px; /* 增加最大高度 */
}

.table-container {
    flex: 1;
    overflow: hidden;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    background: #fff;
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 350px; /* 大幅增加表格最小高度 */
    max-height: 400px; /* 增加表格最大高度 */
    margin-top: 10px; /* 添加表格容器顶部间距 */
}

/* 表格卡片间距优化 */
.table-card .el-card__body {
    display: flex;
    flex-direction: column;
    height: 100% !important;
    flex: 1;
    padding: 15px 15px 10px 15px; /* 进一步减少内边距 */
    overflow: hidden;
}

.responsive-table {
    height: 100% !important;
    overflow: hidden;
    flex: 1;
    display: flex;
    flex-direction: column;
    max-height: 380px; /* 大幅增加表格最大高度限制 */
}

/* 强制表格充满整个容器 */
.responsive-table .el-table {
    width: 100% !important;
    height: 100% !important;
    border-radius: 4px;
    overflow: hidden;
}

/* 表格头部和主体宽度 */
.responsive-table .el-table .el-table__header,
.responsive-table .el-table .el-table__body {
    width: 100% !important;
}

/* 表格头部固定高度 */
.responsive-table .el-table__header-wrapper {
    overflow: hidden;
    height: 40px !important;
}

/* 表格主体显示更多行 - 利用增加的高度空间 */
.responsive-table .el-table__body-wrapper {
    height: calc(12 * 40px) !important; /* 从7行增加到12行 */
    max-height: calc(12 * 40px) !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

/* 表格行高固定 */
.responsive-table .el-table .el-table__row {
    height: 40px !important; /* 固定行高保持紧凑 */
    min-height: 40px !important;
    max-height: 40px !important;
}

/* 表格容器内边距 */
.table-container {
    flex: 1;
    overflow: hidden;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    background: #fff;
    display: flex;
    flex-direction: column;
    height: 100%;
    margin: 0; /* 移除额外边距，依靠card内边距 */
    width: 100%; /* 确保表格容器充满整个宽度 */
}

/* 确保表格行高一致 */
.responsive-table .el-table .el-table__cell {
    padding: 8px 4px !important; /* 调整padding保持紧凑 */
    vertical-align: middle !important;
}

/* 表格列宽自适应优化 */
.responsive-table .el-table__header-wrapper table,
.responsive-table .el-table__body-wrapper table {
    width: 100% !important;
    table-layout: auto !important; /* 改为自动布局，不强制固定 */
    border-collapse: collapse; /* 避免边框占用额外空间 */
}

/* 表格列自动调整宽度 */
.responsive-table .el-table .el-table__cell {
    box-sizing: border-box;
    white-space: nowrap; /* 防止文字换行，保持表格紧凑 */
    overflow: hidden;
    text-overflow: ellipsis; /* 超出部分显示省略号 */
}

/* 美化滚动条 */
.responsive-table .el-table__body-wrapper::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

.responsive-table .el-table__body-wrapper::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

.responsive-table .el-table__body-wrapper::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

.responsive-table .el-table__body-wrapper::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

/* 图表自适应 */
.map-chart, .timeline-chart {
    width: 100%;
    flex: 1;
    min-height: 400px;
}

/* 切片筛选条响应式 */
.slice-filter-bar {
    margin-bottom: 20px;
}

.filter-content {
    flex-wrap: wrap;
    gap: 20px;
}

/* 响应式断点 */
@media (min-width: 769px) {
    /* 桌面端强制水平布局 */
    .chart-container {
        flex-direction: row !important;
    }
    
    .left-component,
    .right-component {
        flex: 0 0 40% !important;
        width: 40% !important;
        max-width: 40% !important;
    }
    
    .left-component {
        margin-right: 20px !important;
        margin-left: 0 !important;
    }
    
    .right-component {
        margin-left: 20px !important;
        margin-right: 0 !important;
    }
}

@media (max-width: 1200px) {
    .availability-row {
        height: 165px;
        max-height: 165px;
        margin-bottom: 25px;
    }
    
    .table-row {
        display: flex !important;
        flex-direction: row !important;
        align-items: stretch;
        gap: 5px;
        flex-wrap: nowrap !important;
    }
    
    .table-row .el-col {
        display: flex !important;
        flex: 1;
    }
    
    .availability-number {
        font-size: 24px;
    }
    
    .stats-number {
        font-size: 20px;
    }
    
    .digital-time {
        font-size: 20px;
    }
}

@media (max-width: 768px) {
    /* 移动端间距优化 */
    .dashboard-container {
        padding: 10px;
        padding-bottom: 0; /* 移除移动端底部间距 */
        min-height: 100vh; /* 确保移动端也填满视口 */
    }
    
    .responsive-row {
        margin-bottom: 15px;
    }
    
    .responsive-card {
        margin-bottom: 10px;
        max-height: 350px; /* 移动端进一步限制高度 */
    }
    
    .card-header {
        padding: 15px;
        margin-bottom: 15px;
    }
    
    .chart-container {
        flex-direction: column !important; /* 小屏幕时垂直排列 */
        gap: 10px; /* 减少垂直间距 */
        padding: 5px; /* 减少容器内边距 */
        max-height: 200px; /* 移动端进一步限制容器高度 */
    }
    
    .left-component,
    .right-component {
        flex: none; /* 取消flex比例 */
        width: 100% !important; /* 全宽度 */
        margin-bottom: 10px; /* 减少底部间距 */
    }
    
    .slice-visualizer {
        min-height: 300px; /* 增加移动端切片可视化高度 */
        max-height: 350px; /* 增加移动端最大高度 */
        padding: 8px; /* 进一步减少移动端内边距 */
    }
    
    .table-container {
        max-height: 300px; /* 增加移动端表格高度限制 */
    }
    
    .selected-slice-info {
        margin-top: 15px;
        padding: 15px;
    }
    
    .slice-stack {
        width: 70%;
        height: 80%;
        transform: rotateX(10deg) rotateY(-5deg);
    }
    
    .slice-layer {
        height: 85px;
    }
    
    .slice-name {
        font-size: 16px;
        padding: 0 15px;
    }
    
    .slice-tooltip {
        top: -80px;
        left: 50%;
        transform: translateX(-50%);
        animation: fadeInUp 0.3s ease;
    }
    
    .slice-tooltip::after {
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: rgba(0, 0, 0, 0.9);
        border-right-color: transparent;
    }
    
    .availability-row {
        height: 132px;
        max-height: 132px;
        margin-bottom: 20px;
    }
    
    .responsive-card .el-card__body {
        min-height: 400px;
        padding: 15px;
    }
    
    .availability-card .el-card__body {
        min-height: 69px;
    }
    
    .table-card .el-card__body {
        min-height: 266px;
        max-height: 266px;
    }
    
    .responsive-table .el-table__body-wrapper {
        height: calc(5 * 36px) !important;
        max-height: 180px;
    }
    
    .responsive-table .el-table .el-table__row {
        height: 36px;
    }
    
    .map-chart, .timeline-chart {
        min-height: 350px; /* 增加移动端地图和时间线图表高度 */
    }
    
    .availability-number {
        font-size: 12px;
    }
    
    .availability-label {
        font-size: 7px;
    }
    
    .availability-container {
        gap: 2px;
        min-height: 60px;
        padding: 5px 3px;
        flex-wrap: nowrap !important;
        flex-direction: row !important;
    }
    
    .availability-item {
        padding: 6px 3px;
    }
    
    .stats-number {
        font-size: 18px;
    }
    
    .stats-label {
        font-size: 11px;
    }
    
    .digital-time {
        font-size: 18px;
    }
    
    .filter-content {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .filter-section {
        margin-top: 15px;
        width: 100%;
    }
    
    .filter-select {
        width: 120px;
        margin-left: 8px;
    }
    
    .stats-section {
        gap: 20px;
    }
    
    .responsive-row {
        margin-bottom: 15px;
    }
    
    .table-row {
        margin-bottom: 15px;
        display: flex !important;
        flex-direction: row !important;
        align-items: stretch;
        gap: 3px;
        flex-wrap: nowrap !important;
    }
    
    .table-row .el-col {
        display: flex !important;
        margin-bottom: 0;
        flex: 1;
    }
    
    .card-header-title {
        font-size: 16px;
    }
    
    .card-header-desc {
        font-size: 12px;
    }
}

@media (max-width: 480px) {
    .availability-row {
        height: 110px;
        max-height: 110px;
        margin-bottom: 15px;
    }
    
    .responsive-card .el-card__body {
        min-height: 350px;
        padding: 10px;
    }
    
    .availability-card .el-card__body {
        min-height: 100px;
    }
    
    .table-row {
        display: block;
    }
    
    .table-row .el-col {
        display: block;
        margin-bottom: 10px;
    }
    
    .table-card .el-card__body {
        min-height: 320px;
        max-height: 320px;
    }
    
    .responsive-table .el-table__body-wrapper {
        height: calc(6 * 32px) !important;
        max-height: 192px;
    }
    
    .responsive-table .el-table .el-table__row {
        height: 32px;
    }
    
    .map-chart, .timeline-chart {
        min-height: 250px;
    }
    
    .availability-container {
        padding: 5px 3px;
        flex-wrap: nowrap !important;
        flex-direction: row !important;
        min-height: 55px;
        gap: 2px;
    }
    
    .availability-item {
        flex: 1;
        min-width: 36px;
        padding: 5px 2px;
        font-size: 9px;
    }
    
    .availability-number {
        font-size: 12px;
        margin-bottom: 3px;
    }
    
    .availability-label {
        font-size: 7px;
    }
    
    .stats-section {
        gap: 15px;
        flex-wrap: wrap;
    }
    
    .stats-number {
        font-size: 16px;
    }
    
    .stats-label {
        font-size: 10px;
    }
    
    .card-header-title {
        font-size: 14px;
    }
    
    .card-header-desc {
        font-size: 11px;
    }
    
    .slice-filter-bar {
        padding: 10px 15px;
    }
    
    .filter-section {
        justify-content: space-between;
    }
    
    .filter-select {
        width: 100px;
        margin-left: 5px;
    }
    
    .filter-label {
        font-size: 12px;
    }
}

/* 确保容器使用flex布局 */
.card-header {
    flex-shrink: 0;
}

.responsive-card .el-card__body > div:last-child {
    flex: 1;
    display: flex;
    flex-direction: column;
}

/* 表格列响应式调整 */
@media (max-width: 768px) {
    .el-table .el-table__cell {
        padding: 6px 3px;
    }
    
    .el-table .cell {
        font-size: 12px;
    }
    
    .responsive-table .el-table .el-table__row {
        height: 36px;
    }
}

@media (max-width: 480px) {
    .el-table .el-table__cell {
        padding: 4px 2px;
    }
    
    .el-table .cell {
        font-size: 11px;
    }
    
    .responsive-table .el-table .el-table__row {
        height: 32px;
    }
    
    .el-tag {
        font-size: 10px;
        padding: 0 4px;
        height: 20px;
        line-height: 18px;
    }
}

/* ping探测列表样式 */
.header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    width: 100%;
}

.header-left {
    flex: 1;
}

.header-right {
    display: flex;
    align-items: center;
    margin-top: 5px;
}

.ping-count {
    font-size: 14px;
    font-weight: bold;
    color: #1890ff;
    background: #e6f7ff;
    padding: 4px 12px;
    border-radius: 12px;
    border: 1px solid #91d5ff;
    white-space: nowrap;
}

.table-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    flex: 1;
}

.ping-list {
    flex: 1;
    overflow-y: auto;
    padding: 10px 12px; /* 减少内边距 */
    height: 100%;
    min-height: 350px; /* 大幅增加ping列表高度 */
    max-height: 400px; /* 增加最大高度以充分利用空间 */
}

.ping-item {
    padding: 12px 15px; /* 增加内边距使项目更高 */
    margin-bottom: 8px; /* 稍微增加项目间距 */
    border: 1px solid #e8e8e8;
    border-radius: 4px; /* 稍微减小圆角 */
    background: #fafafa;
    transition: all 0.2s ease;
}

.ping-item:hover {
    background: #f0f0f0;
    border-color: #d0d0d0;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 增加阴影效果 */
}

.ping-item:last-child {
    margin-bottom: 0; /* 完全移除最后一项的底部间距 */
}

.ping-endpoints {
    text-align: center;
}

.ping-text {
    font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
    font-size: 13px;
    font-weight: 600;
    color: #333;
    background: #fff;
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid #ddd;
    display: inline-block;
    min-width: 320px;
    word-break: break-all;
    line-height: 1.4;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.loading-text, .empty-text {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #999;
    font-size: 14px;
    min-height: 380px;
}

.loading-text {
    color: #1890ff;
}

.empty-text {
    color: #bfbfbf;
}

/* 重试按钮样式 */
.retry-section {
    margin-top: 8px;
}

.retry-section .el-button {
    font-size: 12px;
    padding: 4px 8px;
}
</style>
