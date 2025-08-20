<template>
    <div class="dashboard-container">
        <!-- 切片筛选条 -->
        <div class="slice-filter-bar">
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
                </div>
                <div class="filter-section">
                    <span class="filter-label">切片选择</span>
                    <el-select
                        v-model="selectedSlice"
                        placeholder="选择切片"
                        @change="handleSliceChange"
                        size="small"
                        class="filter-select"
                        filterable
                        clearable
                    >
                        <el-option 
                            v-for="slice in networkSlices" 
                            :key="slice.id"
                            :label="slice.name" 
                            :value="slice.id" 
                        />
                    </el-select>
                </div>
            </div>
        </div>

        <el-row :gutter="20" class="responsive-row chart-row">
              <el-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
                <el-card shadow="hover" class="responsive-card chart-card map-slice-card beautify-map-card" style="height:1000px;width:100%;">
                    <div class="card-header beautify-card-header" style="height:60px;">
                        <p class="card-header-title beautify-title">数据大盘</p>
                    </div>
                    <div class="chart-container" style="height:720px;width:100%;">
                        <!-- 地图/拓扑占满整个卡片 -->
                        <div class="full-map-component">
                            <div class="map-container">
                                <v-chart 
                                    class="beautify-map-chart" 
                                    :option="viewMode === 'geographic' ? enhancedMapOptions : topologyOptions" 
                                    @click="handleMapClick"
                                    :key="viewMode"
                                />
                                <!-- 地图内浮动切换按钮 -->
                                <div class="floating-view-switcher">
                                    <div class="floating-buttons">
                                        <el-button 
                                            :type="viewMode === 'geographic' ? 'primary' : 'default'"
                                            size="small"
                                            @click="viewMode = 'geographic'"
                                            class="floating-btn"
                                        >
                                            地理
                                        </el-button>
                                        <el-button 
                                            :type="viewMode === 'topology' ? 'primary' : 'default'"
                                            size="small"
                                            @click="viewMode = 'topology'"
                                            class="floating-btn"
                                        >
                                            拓扑
                                        </el-button>
                                        <el-button 
                                            type="info"
                                            size="small"
                                            @click="showPingListPopup = true"
                                            class="floating-btn"
                                        >
                                            探测列表
                                        </el-button>
                                    </div>
                                    <div class="floating-description">
                                        {{ viewMode === 'geographic' ? '地理视图' : '拓扑视图' }}
                                    </div>
                                </div>
                                <!-- 切片探测列表弹窗 -->
                                <el-dialog 
                                    v-model="showPingListPopup" 
                                    title="当前切片探测列表" 
                                    width="720px" 
                                    :close-on-click-modal="true" 
                                    :append-to-body="true"
                                    :z-index="9999"
                                    :modal="true"
                                    class="ping-list-dialog"
                                >
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
                                </el-dialog>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <!-- 链路时延浮窗 - 移到行级别以避免被表格遮盖 -->
            <transition name="fade">
                <div v-if="showDelayPopup && selectedRoute && selectedRoute !== 'all'" class="delay-popup" :style="delayPopupStyle">
                    <div class="popup-title">24小时时延</div>
                    <v-chart
                        :option="timelineOptions"
                        style="width: 420px; height: 280px; margin-top: 10px;"
                    />
                    <el-button size="mini" type="text" @click="showDelayPopup = false" style="margin-top:12px; font-size: 16px;">关闭</el-button>
                </div>
            </transition>
            <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
                <el-card shadow="hover" class="responsive-card table-card" style="height:600px;width:100%;">
                    <div class="card-header beautify-card-header" style="height:60px;">
                        <p class="card-header-title beautify-title">故障报警</p>
                    </div>
                    <div class="table-container" style="height:720px;width:100%;">
                        <el-table 
                            :data="currentIssuesData" 
                            style="width: 100%; height: 100%;" 
                            class="responsive-table"
                            @row-click="handleIssueRowClick"
                            :row-style="{ cursor: 'pointer' }"
                            :key="`table-${selectedSlice}`"
                        >
                            <el-table-column prop="id" label="问题ID" min-width="60" />
                            <el-table-column prop="type" label="问题类型" min-width="70">
                                <template #default="scope">
                                    <el-tag 
                                        :type="getIssueTypeColor(scope.row.type)"
                                        :class="{ 'two-line-tag': scope.row.type === '延迟下降' }"
                                    >
                                        <span v-if="scope.row.type === '延迟下降'" style="line-height: 1.1; text-align: center; font-size: 10px;">
                                            延迟<br/>下降
                                        </span>
                                        <span v-else>
                                            {{ scope.row.type }}
                                        </span>
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="description" label="问题描述" min-width="100"/>
                            <el-table-column prop="slice" label="所属切片" min-width="80" />
                            <el-table-column prop="location" label="位置" min-width="80">
                                <template #default="scope">
                                    {{ formatLinkNameFromRow(scope.row) }}
                                </template>
                            </el-table-column>
                            <el-table-column prop="createTime" label="发现时间" min-width="80">
                                <template #default="scope">
                                    {{ formatShortTime(scope.row.createTime) }}
                                </template>
                            </el-table-column>
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
        </el-row>
        <el-row :gutter="5" class="responsive-row table-row">
        </el-row>
      
    </div>
</template>

<script setup lang="ts" name="dashboard">
// 当前切片探测列表弹窗
import { ref as vueRef } from 'vue';
const showPingListPopup = vueRef(false);

// 处理地图链路点击，弹出浮窗
const handleMapClick = (params) => {
    // 支持 geo-lines 和 graph-edge 两种点击
    let isLine = false;
    let routeName = '';
    if (params.seriesType === 'lines' && params.data && params.data.name) {
        isLine = true;
        routeName = params.data.name;
    } else if (params.dataType === 'edge' && params.data && params.data.source && params.data.target) {
        isLine = true;
        routeName = params.data.name || `${params.data.source}↔${params.data.target}`;
    }
    if (isLine) {
        selectedRoute.value = routeName;
        showDelayPopup.value = true;
        // 浮窗定位到鼠标点击处
        nextTick(() => {
            if (params.event && params.event.event) {
                const { offsetX, offsetY } = params.event.event;
                // 获取地图容器的实际偏移
                const mapEl = document.querySelector('.beautify-map-chart');
                let mapRect = { left: 0, top: 0 };
                if (mapEl) mapRect = mapEl.getBoundingClientRect();
                // 浮窗宽高应与样式保持一致
                const popupW = 420, popupH = 300;
                // 右移60px
                let left = mapRect.left + offsetX - popupW / 2 + 360;
                let top = mapRect.top + offsetY - popupH / 2;
                // 防止浮窗超出右下边界
                const winW = window.innerWidth;
                const winH = window.innerHeight;
                if (left + popupW > winW) left = winW - popupW - 16;
                if (left < 0) left = 16;
                if (top + popupH > winH) top = winH - popupH - 16;
                if (top < 0) top = 16;
                delayPopupStyle.value = {
                    position: 'fixed',
                    left: left + 'px',
                    top: top + 'px',
                    zIndex: 9999
                };
            } else {
                delayPopupStyle.value = { left: '65%', top: '30%', position: 'fixed', zIndex: 9999 };
            }
        });
    } else {
        showDelayPopup.value = false;
    }
    // 其他类型点击不弹窗
};

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
const viewMode = ref('topology'); // 'geographic' 或 'topology' - 默认为拓扑视图

// 地图聚焦相关变量
const mapCenter = ref([104, 35]); // 地图中心坐标
const mapZoom = ref(1.5); // 地图缩放级别

// 3D切片可视化相关变量（部分已废弃）
const selectedSlice = ref('physical-network'); // 默认选择物理网络，使用数据库中的实际名称
const isSliceSwitching = ref(false);

// 网络拓扑数据
const networkTopology = ref(null);
const isTopologyLoading = ref(true);
const allSliceTopologies = ref({}); // 存储所有切片的拓扑数据


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

// 链路时延浮窗相关
import { nextTick } from 'vue';
const showDelayPopup = ref(false);
const delayPopupStyle = ref({});
const currentLinkDelay = ref(null);

// 计算当前选中链路的时延数据
watch([selectedRoute, realDelayData], ([route, delayList]) => {
    if (!route || route === 'all' || !Array.isArray(delayList) || delayList.length === 0) {
        currentLinkDelay.value = null;
        return;
    }
    // 过滤出该链路的所有时延数据
    // 标准化函数，去除空格、转小写
    const normalize = s => (s || '').replace(/\s+/g, '').toLowerCase();
    const [src, dst] = route.split('-').map(normalize);
    const linkDelays = delayList.filter(item => {
        const s1 = normalize(item.src), d1 = normalize(item.dst);
        return (s1 === src && d1 === dst) || (s1 === dst && d1 === src);
    });
    if (!linkDelays.length) {
        currentLinkDelay.value = null;
        return;
    }
    // 计算平均、最大、最小
    const delays = linkDelays.map(item => typeof item.delay === 'string' ? parseFloat(item.delay) : item.delay).filter(v => !isNaN(v));
    if (!delays.length) {
        currentLinkDelay.value = null;
        return;
    }
    const avg = Math.round(delays.reduce((a, b) => a + b, 0) / delays.length * 100) / 100;
    const max = Math.max(...delays);
    const min = Math.min(...delays);
    currentLinkDelay.value = { avgDelay: avg, maxDelay: max, minDelay: min };
});

// 处理问题表格行点击事件
const handleIssueRowClick = async (row) => {
    console.log('点击问题行:', row);
    
    // 1. 切换到对应的切片 - 使用selectSlice确保平滑过渡
    if (row.slice) {
        // 根据切片名称找到对应的切片ID
        const targetSlice = networkSlices.value.find(slice => slice.name === row.slice);
        if (targetSlice) {
            console.log('切换到切片:', targetSlice.id);
            
            // 使用selectSlice函数来确保平滑过渡
            selectSlice(targetSlice.id);
            
            // 等待切片切换完成
            await nextTick();
        }
    }
    
    // 2. 切换到拓扑视图（而不是地理视图）
    viewMode.value = 'topology';
    
    // 3. 聚焦到对应的链路
    if (row.location) {
        await focusOnLink(row.location);
    }
};

// 聚焦到指定链路
const focusOnLink = async (location) => {
    console.log('聚焦到链路:', location);
    
    // 等待视图切换完成
    await nextTick();
    
    try {
        // 根据位置ID找到对应的城市坐标
        const locationParts = location.split('-');
        if (locationParts.length >= 2) {
            const city1Id = locationParts[0]; // 保持为字符串，不强制转换
            const city2Id = locationParts[1]; // 保持为字符串，不强制转换
            
            // 从当前切片的城市数据中查找坐标
            const currentSliceInfo = selectedSliceInfo.value;
            if (currentSliceInfo && currentSliceInfo.filename) {
                const sliceKey = currentSliceInfo.filename.replace('.json', '');
                const sliceData = allSliceTopologies.value[sliceKey];
                
                if (sliceData && sliceData.cities) {
                    // 尝试多种匹配方式：ID匹配（字符串和数字）、名称匹配
                    const city1 = sliceData.cities.find(c => 
                        String(c.id) === String(city1Id) || 
                        c.id === parseInt(city1Id) || 
                        c.name === city1Id
                    );
                    const city2 = sliceData.cities.find(c => 
                        String(c.id) === String(city2Id) || 
                        c.id === parseInt(city2Id) || 
                        c.name === city2Id
                    );
                    
                    if (city1 && city2) {
                        // 计算两个城市的中点坐标
                        const centerLng = (city1.coord[0] + city2.coord[0]) / 2;
                        const centerLat = (city1.coord[1] + city2.coord[1]) / 2;
                        
                        // 设置地图中心为链路中点
                        mapCenter.value = [centerLng, centerLat];
                        
                        // 设置适当的缩放级别
                        mapZoom.value = 3;
                        
                        console.log(`聚焦到链路中点: [${centerLng}, ${centerLat}] (${city1.name} ↔ ${city2.name})`);
                    } else {
                        console.warn(`未找到城市坐标信息: ${city1Id} -> ${city1 ? '找到' : '未找到'}, ${city2Id} -> ${city2 ? '找到' : '未找到'}`);
                        console.log('可用城市列表:', sliceData.cities.map(c => ({ id: c.id, name: c.name })));
                    }
                } else {
                    console.warn('未找到切片数据');
                }
            }
        }
    } catch (error) {
        console.error('聚焦链路时出错:', error);
    }
};

// 重置地图视图
const resetMapView = () => {
    mapCenter.value = [104, 35];
    mapZoom.value = 1.5;
    console.log('重置地图视图');
};

// 网络切片数据 - 从配置文件动态加载
const networkSlices = ref([]);

// 加载切片配置
const loadSlicesConfiguration = async () => {
    try {
        const response = await fetch('/mock/total_slices.json');
        const data = await response.json();
        // 直接使用配置文件中的顺序，不再按priority排序
        networkSlices.value = data.slices;
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

// 预定义的颜色调色板
const colorPalette = [
    '#8c8c8c',   // 灰色
    '#52c41a',   // 绿色 
    '#1890ff',   // 蓝色
    '#ff4d4f',   // 红色
    '#722ed1',   // 紫色
    '#13c2c2',   // 青色
    '#faad14',   // 橙色
    '#f759ab',   // 粉色
    '#a0d911',   // 青绿色
    '#40a9ff'    // 浅蓝色
];

// 根据索引自动分配颜色
const getSliceColor = (index) => {
    return colorPalette[index % colorPalette.length];
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
                    return { success: true, sliceId, data };
                } else {
                    console.warn(`切片拓扑文件不存在: ${filename}`);
                    return { success: false, filename, error: 'File not found' };
                }
            } catch (error) {
                console.error(`加载切片拓扑失败: ${filename}`, error);
                return { success: false, filename, error: error.message };
            }
        });
        
        // 使用 Promise.allSettled 替代 Promise.all，这样单个失败不会影响其他
        const results = await Promise.allSettled(loadPromises);
        
        // 处理结果，只记录失败的情况但不阻止继续执行
        results.forEach((result, index) => {
            if (result.status === 'rejected') {
                console.error(`切片拓扑加载Promise失败: ${sliceFiles[index]}`, result.reason);
            } else if (result.value && !result.value.success) {
                console.warn(`切片拓扑加载失败: ${result.value.filename}`, result.value.error);
            }
        });
        
        allSliceTopologies.value = topologies;
        
        // 设置默认显示的拓扑为物理网络（第一个切片）
        const physicalSlice = networkSlices.value.find(slice => slice.id === 'physical-network');
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

// 格式化链路名称显示 - 只在指定切片拓扑查找ID对应的城市名称
// sliceKey: 切片id或文件名（如 physical-network）
const formatLinkName = (linkId, sliceKey) => {
    try {
        if (!linkId || linkId === 'all') {
            return linkId;
        }

        // 解析链路ID (格式: "BJ001-SH002" 或 "0-1")
        const parts = linkId.split('-');
        if (parts.length !== 2) {
            return linkId; // 如果格式不正确，返回原始ID
        }

        const [sourceId, targetId] = parts;

        // 只在指定切片拓扑查找
        let topo = null;
        if (sliceKey && allSliceTopologies.value && allSliceTopologies.value[sliceKey]) {
            topo = allSliceTopologies.value[sliceKey];
        } else if (networkTopology.value) {
            topo = networkTopology.value;
        }
        
        if (topo && Array.isArray(topo.cities)) {
            console.log(`查找城市 ${sourceId} 和 ${targetId} 在切片 ${sliceKey}`);
            console.log(`可用城市:`, topo.cities.map(c => ({id: c.id, name: c.name})));
            
            // 先尝试通过 ID 匹配
            let sourceCity = topo.cities.find(city => String(city.id) === String(sourceId));
            let targetCity = topo.cities.find(city => String(city.id) === String(targetId));
            
            console.log(`ID匹配结果: ${sourceId} -> ${sourceCity ? sourceCity.name : '未找到'}, ${targetId} -> ${targetCity ? targetCity.name : '未找到'}`);
            
            // 如果通过 ID 找不到，尝试通过 name 匹配（防止ID和name混用的情况）
            if (!sourceCity) {
                sourceCity = topo.cities.find(city => String(city.name) === String(sourceId));
                if (sourceCity) console.log(`通过名称找到源城市: ${sourceId} -> ${sourceCity.name}`);
            }
            if (!targetCity) {
                targetCity = topo.cities.find(city => String(city.name) === String(targetId));
                if (targetCity) console.log(`通过名称找到目标城市: ${targetId} -> ${targetCity.name}`);
            }
            
            // 如果找到了对应的城市，返回城市名称
            if (sourceCity && targetCity) {
                return `${sourceCity.name} ↔ ${targetCity.name}`;
            }
            
            // 如果只找到一个城市，尝试将另一个作为城市名直接显示
            if (sourceCity && !targetCity) {
                return `${sourceCity.name} ↔ ${targetId}`;
            }
            if (!sourceCity && targetCity) {
                return `${sourceId} ↔ ${targetCity.name}`;
            }
        } else {
            console.warn(`未找到切片拓扑数据或城市数据: sliceKey=${sliceKey}, topo=`, topo);
        }
        
        // 如果找不到对应的城市，返回原始ID
        return linkId;
    } catch (error) {
        // 如果格式化过程中出现任何错误，返回原始ID而不影响其他条目
        console.warn(`格式化链路名称时出错: ${linkId}`, error);
        return linkId || 'N/A';
    }
};

// 从表格行数据格式化链路名称 - 专门处理表格行的情况
const formatLinkNameFromRow = (row) => {
    try {
        if (!row || !row.location) {
            return 'N/A';
        }
        
        let sliceKey = null;
        
        // 优先使用行数据中的切片信息
        if (row.slice) {
            // 如果row.slice是切片名称，需要转换为sliceKey
            const sliceInfo = networkSlices.value.find(slice => slice.name === row.slice);
            if (sliceInfo) {
                sliceKey = sliceInfo.filename ? sliceInfo.filename.replace('.json', '') : sliceInfo.id;
            } else {
                // 如果找不到匹配的切片，尝试几种可能的切片key格式
                const possibleKeys = [
                    row.slice,
                    row.slice.toLowerCase().replace(/\s+/g, '-'),
                    row.slice.toLowerCase().replace(/\s+/g, '_')
                ];
                
                for (const key of possibleKeys) {
                    if (allSliceTopologies.value && allSliceTopologies.value[key]) {
                        sliceKey = key;
                        break;
                    }
                }
                
                // 如果还是找不到，使用row.slice作为key
                if (!sliceKey) {
                    sliceKey = row.slice;
                }
            }
        }
        
        // 如果没有找到切片key，使用当前选中的切片
        if (!sliceKey) {
            const currentSliceInfo = selectedSliceInfo.value;
            if (currentSliceInfo && currentSliceInfo.filename) {
                sliceKey = currentSliceInfo.filename.replace('.json', '');
            } else {
                sliceKey = selectedSlice.value;
            }
        }
        
        console.log(`格式化表格行位置: ${row.location}, 行切片: ${row.slice}, 使用切片key: ${sliceKey}`);
        console.log(`可用的切片拓扑:`, Object.keys(allSliceTopologies.value || {}));
        
        const result = formatLinkName(row.location, sliceKey);
        console.log(`格式化结果: ${result}`);
        return result;
    } catch (error) {
        console.warn(`格式化表格行位置时出错:`, error);
        return row.location || 'N/A';
    }
};

// 保留原来的函数名作为兼容
const loadNetworkTopology = loadAllSliceTopologies;



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

    // 获取有问题的链路位置信息
    const getProblemLinks = () => {
        const problemLinks = new Set();
        currentIssuesData.value.forEach(issue => {
            // 只处理待处理的中断和延迟下降问题
            if ((issue.type === '中断' || issue.type === '延迟下降') && 
                issue.status === '待处理' && issue.location) {
                problemLinks.add(issue.location);
            }
        });
        return problemLinks;
    };

    const problemLinks = getProblemLinks();

    // 检查连接是否有问题，返回问题详情
    const getConnectionProblemInfo = (connection) => {
        if (!connection.name) return null;
        
        const connectionId = connection.name;
        
        // 查找匹配的问题
        for (const issue of currentIssuesData.value) {
            if ((issue.type === '中断' || issue.type === '延迟下降') && 
                (issue.status === '待处理' || issue.status === '处理中') && 
                issue.location) {
                
                const problemLocationStr = String(issue.location);
                if (connectionId.includes(problemLocationStr) || problemLocationStr.includes(connectionId)) {
                    return {
                        type: issue.type,
                        status: issue.status,
                        severity: issue.severity
                    };
                }
            }
        }
        return null;
    };

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


    return {
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                if (params.seriesType === 'lines') {
                    const conn = processedConnections.find(c => c.name === params.data.name);
                    let tooltipContent = `<div style="font-weight: bold;">${formatLinkName(params.data.name, selectedSlice)}</div>`;
                    
                    // 检查是否有问题信息
                    if (params.data.problemInfo) {
                        const issue = currentIssuesData.value.find(item => {
                            if (!item.location) return false;
                            const problemLocation = String(item.location);
                            const connectionName = params.data.name;
                            // 精确匹配位置信息
                            return connectionName.includes(problemLocation) || problemLocation.includes(connectionName) ||
                                   (connectionName.split('-').length >= 2 && problemLocation.split('-').length >= 2 &&
                                    connectionName.split('-')[0] === problemLocation.split('-')[0] &&
                                    connectionName.split('-')[1] === problemLocation.split('-')[1]);
                        });
                        
                        if (issue) {
                            tooltipContent += `<div style="margin-top: 8px; padding: 8px; background: #fff2f0; border-left: 3px solid #ff4d4f;">`;
                            tooltipContent += `<div style="color: #ff4d4f; font-weight: bold;">⚠️ 警告信息</div>`;
                            tooltipContent += `<div><strong>问题ID:</strong> ${issue.id}</div>`;
                            tooltipContent += `<div><strong>类型:</strong> ${issue.type}</div>`;
                            tooltipContent += `<div><strong>状态:</strong> ${issue.status}</div>`;
                            tooltipContent += `<div><strong>描述:</strong> ${issue.description}</div>`;
                            tooltipContent += `<div><strong>严重性:</strong> ${issue.severity}</div>`;
                            tooltipContent += `</div>`;
                        }
                    } else if (conn) {
                        // 正常连接信息
                        tooltipContent += `<div>IP: ${conn.IP || 'N/A'}</div>`;
                        tooltipContent += `<div>IPv6: ${conn.IPv6 || 'N/A'}</div>`;
                    }
                    
                    return tooltipContent;
                } else if (params.seriesType === 'scatter') {
                    // 检查是否是警告标记
                    if (params.data.name && params.data.name.includes('警告') && params.data.issueInfo) {
                        const issue = params.data.issueInfo;
                        let tooltipContent = `<div style="font-weight: bold; color: #ff4d4f;">⚠️ 问题警告</div>`;
                        tooltipContent += `<div><strong>问题ID:</strong> ${issue.id}</div>`;
                        tooltipContent += `<div><strong>报告时间:</strong> ${issue.createTime}</div>`;
                        return tooltipContent;
                    } else {
                        return `<div style="font-weight: bold;">${params.data.name}</div>`;
                    }
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
                areaColor: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 1,
                    y2: 1,
                    colorStops: [
                        { offset: 0, color: '#fafafa' },
                        { offset: 0.5, color: '#f5f5f5' },
                        { offset: 1, color: '#f0f0f0' }
                    ]
                },
                borderColor: '#d9d9d9',
                borderWidth: 1.5,
                shadowColor: 'rgba(0, 0, 0, 0.1)',
                shadowBlur: 6,
                shadowOffsetX: 1,
                shadowOffsetY: 1
            },
            emphasis: {
                itemStyle: {
                    areaColor: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 1,
                        y2: 1,
                        colorStops: [
                            { offset: 0, color: '#f5f5f5' },
                            { offset: 0.5, color: '#f0f0f0' },
                            { offset: 1, color: '#e8e8e8' }
                        ]
                    },
                    borderColor: '#bfbfbf',
                    shadowBlur: 8,
                    shadowColor: 'rgba(0, 0, 0, 0.15)'
                }
            }
        },
        series: [
            // 连接线 - 先绘制线条
            {
                name: '网络连接',
                type: 'lines',
                coordinateSystem: 'geo',
                data: adjustedConnections.map((conn, index) => {
                    const problemInfo = getConnectionProblemInfo(conn);
                    
                    let lineColor = {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 1,
                        y2: 0,
                        colorStops: [
                            { offset: 0, color: '#52c41a' },
                            { offset: 0.5, color: '#73d13d' },
                            { offset: 1, color: '#52c41a' }
                        ]
                    };
                    let lineWidth = 2.5;
                    let showWarning = false;
                    let warningColor = '#ff4d4f';
                    let shadowColor = 'rgba(82, 196, 26, 0.3)';
                    let shadowBlur = 3;
                    
                    if (problemInfo) {
                        lineWidth = 4; // 问题链路加粗
                        showWarning = true;
                        
                        if (problemInfo.status === '处理中') {
                            // 处理中状态：橙色渐变
                            lineColor = {
                                type: 'linear',
                                x: 0,
                                y: 0,
                                x2: 1,
                                y2: 0,
                                colorStops: [
                                    { offset: 0, color: '#fa8c16' },
                                    { offset: 0.5, color: '#ffa940' },
                                    { offset: 1, color: '#fa8c16' }
                                ]
                            };
                            warningColor = '#fa8c16';
                            shadowColor = 'rgba(250, 140, 22, 0.5)';
                            shadowBlur = 6;
                        } else if (problemInfo.status === '待处理') {
                            // 待处理状态：红色渐变
                            lineColor = {
                                type: 'linear',
                                x: 0,
                                y: 0,
                                x2: 1,
                                y2: 0,
                                colorStops: [
                                    { offset: 0, color: '#ff4d4f' },
                                    { offset: 0.5, color: '#ff7875' },
                                    { offset: 1, color: '#ff4d4f' }
                                ]
                            };
                            warningColor = '#ff4d4f';
                            shadowColor = 'rgba(255, 77, 79, 0.6)';
                            shadowBlur = 8;
                        }
                    }
                    
                    return {
                        name: conn.name,
                        coords: conn.coords,
                        // 添加问题信息到数据中，供tooltip使用
                        problemInfo: problemInfo,
                        lineStyle: {
                            color: lineColor,
                            width: lineWidth,
                            type: 'solid',
                            shadowColor: shadowColor,
                            shadowBlur: shadowBlur,
                            shadowOffsetX: 1,
                            shadowOffsetY: 1
                        },
                        effect: {
                            show: showWarning,
                            period: 1.5,
                            trailLength: 0,
                            symbol: 'circle',
                            symbolSize: 18,
                            color: warningColor,
                            constantSpeed: 40
                        }
                    };
                }),
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
                symbolSize: 14,
                itemStyle: {
                    color: {
                        type: 'radial',
                        x: 0.5,
                        y: 0.5,
                        r: 0.5,
                        colorStops: [
                            { offset: 0, color: '#595959' },
                            { offset: 0.7, color: '#434343' },
                            { offset: 1, color: '#262626' }
                        ]
                    },
                    borderColor: '#ffffff',
                    borderWidth: 2,
                    shadowBlur: 4,
                    shadowColor: 'rgba(89, 89, 89, 0.4)',
                    shadowOffsetX: 1,
                    shadowOffsetY: 1
                },
                emphasis: {
                    label: {
                        show: true, // 悬停时显示标签
                        fontSize: 16,
                        fontWeight: 'bold'
                    },
                    itemStyle: {
                        color: {
                            type: 'radial',
                            x: 0.5,
                            y: 0.5,
                            r: 0.5,
                            colorStops: [
                                { offset: 0, color: '#6b6b6b' },
                                { offset: 0.7, color: '#525252' },
                                { offset: 1, color: '#363636' }
                            ]
                        },
                        borderColor: '#ffffff',
                        borderWidth: 3,
                        shadowBlur: 8,
                        shadowColor: 'rgba(89, 89, 89, 0.6)',
                        scale: 1.3
                    }
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
                }
            },
            // 警告感叹号系列 - 在有问题的链路中点显示
            {
                name: '警告标记',
                type: 'scatter',
                coordinateSystem: 'geo',
                symbol: 'circle',
                symbolSize: 24,
                itemStyle: {
                    color: {
                        type: 'radial',
                        x: 0.5,
                        y: 0.5,
                        r: 0.5,
                        colorStops: [
                            { offset: 0, color: '#ffffff' },
                            { offset: 0.7, color: '#fff2f0' },
                            { offset: 1, color: '#ffebe8' }
                        ]
                    },
                    borderColor: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 1,
                        y2: 1,
                        colorStops: [
                            { offset: 0, color: '#ff4d4f' },
                            { offset: 1, color: '#cf1322' }
                        ]
                    },
                    borderWidth: 3,
                    shadowBlur: 8,
                    shadowColor: 'rgba(255, 77, 79, 0.5)',
                    shadowOffsetX: 2,
                    shadowOffsetY: 2
                },
                data: adjustedConnections.filter(conn => {
                    const problemInfo = getConnectionProblemInfo(conn);
                    return problemInfo !== null;
                }).map(conn => {
                    // 使用 adjustedConnections 中已经微调后的坐标计算中点
                    const startCoord = conn.coords[0];
                    const endCoord = conn.coords[1];
                    const midLng = (startCoord[0] + endCoord[0]) / 2;
                    const midLat = (startCoord[1] + endCoord[1]) / 2;
                    
                    // 找到对应的问题详细信息
                    const issue = currentIssuesData.value.find(item => {
                        if (!item.location) return false;
                        const problemLocation = String(item.location);
                        const connectionName = conn.name;
                        return connectionName.includes(problemLocation) || problemLocation.includes(connectionName) ||
                               (connectionName.split('-').length >= 2 && problemLocation.split('-').length >= 2 &&
                                connectionName.split('-')[0] === problemLocation.split('-')[0] &&
                                connectionName.split('-')[1] === problemLocation.split('-')[1]);
                    });
                    
                    return {
                        name: `${conn.name}-警告`,
                        coord: [midLng, midLat],
                        value: [midLng, midLat, '⚠️'],
                        // 添加问题详细信息供 tooltip 使用
                        issueInfo: issue ? {
                            id: issue.id,
                            createTime: issue.createTime,
                            type: issue.type,
                            status: issue.status
                        } : null
                    };
                }).filter(item => item !== undefined),
                label: {
                    show: true,
                    position: 'inside',
                    formatter: '⚠️',
                    fontSize: 14,
                    color: '#ff4d4f',
                    fontWeight: 'bold',
                    textShadowColor: 'rgba(255, 255, 255, 0.8)',
                    textShadowBlur: 2
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 15,
                        shadowColor: 'rgba(255, 77, 79, 0.8)',
                        scale: 1.2,
                        borderWidth: 4,
                        borderColor: '#cf1322'
                    },
                    label: {
                        fontSize: 16,
                        textShadowBlur: 4
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
                },
                myResetView: {
                    show: true,
                    title: '重置视图',
                    icon: 'M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0M12 1v6l3-3M12 23v-6l-3 3',
                    onclick: () => {
                        resetMapView();
                    }
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
        
        // 用 name 作为唯一标识，禁止用 id/index
        // 若 name 有重复，自动加后缀保证唯一
        const nameCount = {};
        nodes = cities.map(city => {
            let uniqueName = city.name;
            if (nameCount[uniqueName]) {
                nameCount[uniqueName]++;
                uniqueName = `${uniqueName}_${nameCount[uniqueName]}`;
            } else {
                nameCount[uniqueName] = 1;
            }
            city._uniqueName = uniqueName;
            return {
                name: uniqueName
            };
        });
        // 连接关系全部用唯一 name
        const allConnections = [];
        sliceConnections.forEach(conn => {
            const points = conn.points;
            if (points.length === 2) {
                const sourceCity = cities.find(c => c.id === points[0]);
                const targetCity = cities.find(c => c.id === points[1]);
                if (sourceCity && targetCity) {
                    allConnections.push({
                        source: sourceCity._uniqueName,
                        target: targetCity._uniqueName,
                        name: `${sourceCity.id}-${targetCity.id}` // 使用ID而不是名称，与地理视图保持一致
                    });
                }
            } else if (points.length > 2) {
                for (let i = 0; i < points.length; i++) {
                    for (let j = i + 1; j < points.length; j++) {
                        const city1 = cities.find(c => c.id === points[i]);
                        const city2 = cities.find(c => c.id === points[j]);
                        if (city1 && city2) {
                            allConnections.push({
                                source: city1._uniqueName,
                                target: city2._uniqueName,
                                name: `${city1.id}-${city2.id}` // 使用ID而不是名称，与地理视图保持一致
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
    }

    console.log('使用的节点数据:', nodes);
    console.log('使用的连接数据:', connections);
    console.log('当前问题数据:', currentIssuesData.value);

    // 检查连接是否有问题，返回问题详情 - 与地理视图使用完全相同的逻辑
    const getConnectionProblemInfo = (connection) => {
        if (!connection.name) return null;
        
        const connectionId = connection.name;
        
        // 查找匹配的问题
        for (const issue of currentIssuesData.value) {
            if ((issue.type === '中断' || issue.type === '延迟下降') && 
                (issue.status === '待处理' || issue.status === '处理中') && 
                issue.location) {
                
                const problemLocationStr = String(issue.location);
                // 使用与地理视图完全相同的匹配逻辑
                if (connectionId.includes(problemLocationStr) || problemLocationStr.includes(connectionId)) {
                    console.log(`拓扑图发现问题连接: ${connectionId} 匹配问题: ${problemLocationStr}`);
                    return {
                        type: issue.type,
                        status: issue.status,
                        severity: issue.severity
                    };
                }
            }
        }
        return null;
    };

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

        // 直接处理连接数据 - 使用 graph 类型的正确语法
        const processedLinks = connections.map((conn) => {
            // 使用与地理视图完全相同的问题检测逻辑
            const problemInfo = getConnectionProblemInfo(conn);
            
            let lineColor = '#00ff00'; // 默认绿色，与地理视图保持一致
            let lineWidth = 3;
            
            if (problemInfo) {
                lineWidth = 6; // 问题链路加粗，与地理视图一致
                
                if (problemInfo.status === '处理中') {
                    // 未知状态：橙色
                    lineColor = '#fa8c16';
                } else if (problemInfo.status === '待处理') {
                    // 不可用/异常状态：红色
                    lineColor = '#ff4d4f';
                }
                console.log(`拓扑图问题连接 ${conn.name} 设置颜色: ${lineColor}`);
            }
            
            // 在 graph 类型中，需要使用 lineStyle 属性
            return {
                source: conn.source,
                target: conn.target,
                name: conn.name,
                lineStyle: {
                    color: lineColor,
                    width: lineWidth,
                    type: 'solid',
                    opacity: problemInfo ? 1 : 0.8,
                    shadowColor: problemInfo ? 'rgba(255, 77, 79, 0.6)' : 'transparent',
                    shadowBlur: problemInfo ? 6 : 0
                },
                label: {
                    show: false  // 不显示标签
                },
                emphasis: {
                    lineStyle: {
                        color: problemInfo ? lineColor : '#666',
                        width: problemInfo ? 9 : 5,
                        shadowBlur: 10,
                        shadowColor: problemInfo ? 'rgba(255, 77, 79, 0.8)' : 'rgba(149, 165, 166, 0.8)'
                    }
                },
                // 保存问题信息供 tooltip 使用
                problemInfo: problemInfo
            };
        });

        console.log('处理后的节点总数:', processedNodes.length);
        console.log('处理后的连接总数:', processedLinks.length);
        console.log('所有节点ID:', processedNodes.map(n => n.id));
        console.log('所有连接源目标:', processedLinks.map(l => `${l.source} -> ${l.target}`));
        console.log('处理后的连接详情:', processedLinks);

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
                            let tooltipContent = `<div style="font-weight: bold;">${formatLinkName(params.data.name, selectedSlice.value)}</div>`;
                            
                            // 使用与地理视图完全相同的逻辑：通过问题数据查找匹配的问题
                            const issue = currentIssuesData.value.find(item => {
                                if (!item.location || !params.data.name) return false;
                                const problemLocation = String(item.location);
                                const connectionName = params.data.name;
                                // 精确匹配位置信息
                                return connectionName.includes(problemLocation) || problemLocation.includes(connectionName) ||
                                       (connectionName.split('-').length >= 2 && problemLocation.split('-').length >= 2 &&
                                        connectionName.split('-')[0] === problemLocation.split('-')[0] &&
                                        connectionName.split('-')[1] === problemLocation.split('-')[1]);
                            });
                            
                            if (issue && (issue.status === '待处理' || issue.status === '处理中')) {
                                tooltipContent += `<div style="margin-top: 8px; padding: 8px; background: #fff2f0; border-left: 3px solid #ff4d4f;">`;
                                tooltipContent += `<div style="color: #ff4d4f; font-weight: bold;">⚠️ 警告信息</div>`;
                                tooltipContent += `<div><strong>问题ID:</strong> ${issue.id}</div>`;
                                tooltipContent += `<div><strong>类型:</strong> ${issue.type}</div>`;
                                tooltipContent += `<div><strong>状态:</strong> ${issue.status}</div>`;
                                tooltipContent += `<div><strong>描述:</strong> ${issue.description}</div>`;
                                tooltipContent += `<div><strong>严重性:</strong> ${issue.severity}</div>`;
                                tooltipContent += `</div>`;
                            }
                            
                            return tooltipContent;
                        } else if (params.seriesType === 'scatter' && params.data.name && params.data.name.includes('警告')) {
                            // 处理警告标记的tooltip
                            const linkName = params.data.name.replace('-警告', '');
                            let tooltipContent = `<div style="font-weight: bold;">${formatLinkName(linkName, selectedSlice.value)}</div>`;
                            
                            const issue = currentIssuesData.value.find(item => {
                                if (!item.location) return false;
                                const problemLocation = String(item.location);
                                // 精确匹配位置信息
                                return linkName.includes(problemLocation) || problemLocation.includes(linkName) ||
                                       linkName.replace('↔', '-') === problemLocation ||
                                       problemLocation.replace('-', '↔') === linkName;
                            });
                            
                            if (issue && (issue.status === '待处理' || issue.status === '处理中')) {
                                tooltipContent += `<div style="margin-top: 8px; padding: 8px; background: #fff2f0; border-left: 3px solid #ff4d4f;">`;
                                tooltipContent += `<div style="color: #ff4d4f; font-weight: bold;">⚠️ 警告信息</div>`;
                                tooltipContent += `<div><strong>问题ID:</strong> ${issue.id}</div>`;
                                tooltipContent += `<div><strong>类型:</strong> ${issue.type}</div>`;
                                tooltipContent += `<div><strong>状态:</strong> ${issue.status}</div>`;
                                tooltipContent += `<div><strong>描述:</strong> ${issue.description}</div>`;
                                tooltipContent += `<div><strong>严重性:</strong> ${issue.severity}</div>`;
                                tooltipContent += `</div>`;
                            }
                            
                            return tooltipContent;
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
                // 移除全局 lineStyle，让每个连接使用自己的样式
                // lineStyle: {
                //     opacity: 0.8,
                //     curveness: 0.1
                // },
                emphasis: {
                    focus: 'adjacency'
                    // 移除全局 emphasis lineStyle，让每个连接使用自己的 emphasis 样式
                    // lineStyle: {
                    //     width: 4,
                    //     opacity: 1
                    // }
                },
                force: {
                    repulsion: 2000,      // 增加节点间斥力，避免重叠
                    gravity: 0.1,         // 减小重力，给节点更多展开空间
                    edgeLength: [80, 200], // 增加边长范围，让连接更明显
                    layoutAnimation: true,
                    friction: 0.6         // 增加摩擦力，稳定布局
                },
                animationDuration: 1000,
                animationEasing: 'cubicOut'
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
    
    // 添加调试信息
    console.log('=== 24小时时延数据调试 ===');
    console.log('原始数据总量:', filteredData ? filteredData.length : 0);
    console.log('当前选中切片:', selectedSlice.value);
    console.log('样本原始数据:', filteredData ? filteredData.slice(0, 3) : []);
    if (filteredData && filteredData.length > 0) {
        console.log('数据中的所有切片名称:', [...new Set(filteredData.map(item => item.slice))]);
    }
    
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
                let title = '';
                if (selectedSlice.value && selectedSlice.value !== 'all') {
                    title += `${selectedSliceInfo.value?.name || ''}切片`;
                }
                if (selectedRoute.value && selectedRoute.value !== 'all') {
                    title += ` - ${formatLinkName(selectedRoute.value, selectedSlice.value)}`;
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
                if (selectedSlice.value && selectedSlice.value !== 'all') {
                    tooltipContent += `<br/>切片: ${selectedSlice.value}`;
                }
                if (selectedRoute.value && selectedRoute.value !== 'all') {
                    tooltipContent += `<br/>链路: ${formatLinkName(selectedRoute.value, selectedSlice.value)}`;
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


// 当前问题数据 - 从加载的警报数据获取
import alertMock from '../../public/mock/alert.json';
const currentIssuesData = computed(() => {
    // 显示所有问题，包括已解决的
    return alertMock.currentIssues;
});

// 选择的切片组（已废弃，保留以防兼容性问题）
const selectedSliceGroup = ref(1);

// 切片组配置（已废弃，保留以防兼容性问题）
const sliceGroups = computed(() => {
    return [];
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

// 过滤后的切片数据（使用动态加载的切片数据）
const filteredSliceData = computed(() => {
    return networkSlices.value;
});

// 切片组变化处理（已废弃，保留以防兼容性问题）
const handleSliceGroupChange = (value: number) => {
    // 不再使用切片组，此函数保留为空以避免错误
};

// 切片选择变化处理
const handleSliceChange = (sliceId: string) => {
    if (sliceId) {
        selectSlice(sliceId);
    }
};

// 问题类型颜色映射
const getIssueTypeColor = (type: string) => {
    // 默认映射
    const colorMap: { [key: string]: string } = {
        '延迟下降': 'warning',
        '中断': 'danger'
    };
    return colorMap[type] || '';
};

// 严重程度颜色映射
const getSeverityColor = (severity: string) => {
    // 默认映射
    const colorMap: { [key: string]: string } = {
        '高': 'danger',
        '中': 'warning',
        '低': 'info'
    };
    return colorMap[severity] || '';
};

// 时间格式化函数 - 转换为简写格式 (YY/MM/DD HH:mm)
const formatShortTime = (dateTime: string) => {
    if (!dateTime) return '';
    try {
        const date = new Date(dateTime);
        const year = date.getFullYear().toString().slice(-2); // 取年份后两位
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hour = date.getHours().toString().padStart(2, '0');
        const minute = date.getMinutes().toString().padStart(2, '0');
        return `${year}/${month}/${day} ${hour}:${minute}`;
    } catch (error) {
        return dateTime; // 如果解析失败，返回原始值
    }
};

// 状态颜色映射
const getStatusColor = (status: string) => {
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


// 切片状态颜色映射
const getSliceStatusColor = (status: string) => {
    const colorMap: { [key: string]: string } = {
        '正常': 'success',
        '告警': 'danger',
        '维护': 'warning'
    };
    return colorMap[status] || '';
};

// 组件挂载时加载网络拓扑数据
onMounted(async () => {
    await loadNetworkTopology();
    loadDelayData(); // 加载实时时延数据
    // 初始化默认切片（物理网络）的拓扑和探测数据
    switchSliceTopology('physical-network');
    
    // 确保初始选择第一个可用切片
    if (networkSlices.value.length > 0) {
        selectSlice(networkSlices.value[0].id);
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
    align-items: center;
    height: 100px;
    padding: 0;
}
</style>
<style scoped>
/* 链路时延浮窗样式优化 */
.delay-popup {
    position: absolute;
    min-width: 460px;
    min-height: 320px;
    background: #fff;
    border: 3px solid #409eff;
    box-shadow: 0 10px 40px rgba(0,0,0,0.32);
    border-radius: 14px;
    padding: 26px 32px 22px 32px;
    color: #222;
    font-size: 17px;
    z-index: 10000; /* 进一步提高 z-index，确保在所有元素之上 */
    pointer-events: auto;
    opacity: 1;
    transition: all 0.18s cubic-bezier(.4,0,.2,1);
}

.delay-popup .popup-title {
    font-size: 20px;
    font-weight: 600;
    color: #409eff;
    margin-bottom: 12px;
    text-align: center;
}
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

/* 确保页面不会超出视口高度，禁止滚动 */
.dashboard-container {
    padding-bottom: 0; /* 移除页面底部间距 */
    height: 100vh; /* 精确使用视口高度 */
    max-height: 100vh; /* 防止超出 */
    overflow: hidden; /* 禁止滚动 */
    gap: 20px; /* 为各行添加间距 */
    padding: 20px; /* 添加整体内边距 */
    box-sizing: border-box; /* 确保padding包含在总高度内 */
}

/* 确保表格行能充满剩余空间 */
.dashboard-container .table-row {
    height: 400px; /* 固定表格行高度 */
}

.card-content {
    text-align: center;
    font-size: 14px;
    color: #999;
    padding: 0 20px;
    height: 100px; /* 固定高度 */
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
    width: 100%;
    height: 100%;
    gap: 2px; /* 进一步减少左右组件之间的间距 */
    align-items: stretch; /* 确保子元素等高 */
    padding: 0; /* 完全移除容器内边距 */
    overflow: hidden; /* 防止内容超出边界 */
}

/* 全宽地图组件样式 */
.full-map-component {
    width: 100%;
    height: 100%;
    overflow: hidden; /* 防止内容超出边界 */
}

.left-component {
    width: 24%; /* 固定左侧宽度 */
    height: 100%;
    align-self: stretch; /* 确保垂直拉伸 */
}

.right-component {
    width: 76%; /* 固定右侧宽度 */
    height: 100%;
    align-self: stretch; /* 确保垂直拉伸 */
}

/* 表格卡片容器 - 确保充满剩余高度 */
.right-component .el-col:last-child {
    height: 100%;
}

/* 地图容器占据全部空间 */
.map-container {
    position: relative;
    height: 100%;
    width: 100%;
    overflow: hidden; /* 防止地图超出边界 */
}

/* 地图图表占据全部空间 - 已移除，使用v-chart默认样式 */

/* 浮动切换按钮样式 */
.floating-view-switcher {
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 200; /* 提高z-index确保显示在最上层 */
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 4px 16px 0 rgba(60, 120, 200, 0.15);
    border: 1px solid rgba(224, 234, 255, 0.8);
    backdrop-filter: blur(8px);
    transition: all 0.3s ease;
}

.floating-view-switcher:hover {
    box-shadow: 0 6px 24px 0 rgba(60, 120, 200, 0.25);
    transform: translateY(-2px);
}

.floating-buttons {
    gap: 6px;
    margin-bottom: 6px;
}

.floating-btn {
    font-size: 12px !important;
    padding: 6px 12px !important;
    height: 28px !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 1px 4px 0 rgba(60, 120, 200, 0.1) !important;
    border: 1px solid #e0eaff !important;
}

.floating-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 8px 0 rgba(60, 120, 200, 0.2) !important;
}

.floating-description {
    text-align: center;
    font-size: 10px;
    color: #6b7a99;
    font-weight: 400;
    margin: 0;
}

/* 3D切片可视化样式 */
.slice-visualizer {
    width: 100%;
    height: 100%;
    border: none;
    border-radius: 20px;
    background: linear-gradient(135deg, 
        rgba(240, 248, 255, 0.8) 0%, 
        rgba(230, 245, 255, 0.6) 50%, 
        rgba(245, 250, 255, 0.8) 100%);
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.08),
        0 8px 32px rgba(0, 0, 0, 0.04);
    padding: 16px;
    overflow: hidden;
    position: relative;
    backdrop-filter: blur(20px);
}

.slice-visualizer::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 20%, rgba(24, 144, 255, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(24, 144, 255, 0.06) 0%, transparent 50%),
        radial-gradient(circle at 40% 60%, rgba(24, 144, 255, 0.04) 0%, transparent 50%);
    pointer-events: none;
    border-radius: inherit;
}

.slice-header {
    text-align: left;
    margin-bottom: 12px;
    position: relative;
    z-index: 10;
    padding: 0 4px;
}

.slice-header h3 {
    margin: 0 0 4px 0;
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.slice-header p {
    margin: 0;
    font-size: 12px;
    color: #64748b;
    font-weight: 500;
}

.slice-stack-container {
    height: calc(100% - 80px); /* 固定高度，减去标题和其他元素的高度 */
    align-items: center;
    justify-content: center;
    perspective: 2000px;
    perspective-origin: 50% 40%;
    position: relative;
    width: 100%;
    overflow: hidden;
    padding: 20px 20px;
    background: linear-gradient(135deg, 
        rgba(24, 144, 255, 0.02) 0%, 
        rgba(24, 144, 255, 0.05) 50%, 
        rgba(24, 144, 255, 0.02) 100%);
    border-radius: 16px;
}

.zoom-controls {
    position: absolute;
    top: 20px;
    right: 20px;
    gap: 8px;
    z-index: 100;
    background: rgba(255, 255, 255, 0.95);
    padding: 8px 12px;
    border-radius: 12px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.zoom-btn {
    width: 34px;
    height: 34px;
    border: 1px solid rgba(24, 144, 255, 0.2);
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.95) 0%, 
        rgba(255, 255, 255, 0.8) 100%);
    border-radius: 8px;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 600;
    color: #1890ff;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}

.zoom-btn:hover {
    background: linear-gradient(135deg, 
        rgba(24, 144, 255, 0.1) 0%, 
        rgba(24, 144, 255, 0.05) 100%);
    border-color: #1890ff;
    color: #1890ff;
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(24, 144, 255, 0.2);
}

.zoom-btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

.slice-stack {
    position: relative;
    width: 80%;
    height: 75%;
    transform-style: preserve-3d;
    transform: rotateX(20deg) rotateY(-15deg);
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.15));
}

.slice-stack:hover {
    transform: rotateX(25deg) rotateY(-20deg) scale(1.02);
}

.slice-layer {
    position: absolute;
    width: 100%;
    height: 30px;
    border: 2px solid transparent;
    border-radius: 16px;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.95) 0%, 
        rgba(255, 255, 255, 0.85) 100%);
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    align-items: center;
    justify-content: center;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.12),
        0 4px 16px rgba(0, 0, 0, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
    opacity: 1;
}

.slice-layer::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, 
        rgba(24, 144, 255, 0.1) 0%, 
        rgba(24, 144, 255, 0.05) 50%,
        rgba(24, 144, 255, 0.1) 100%);
    border-radius: inherit;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.slice-layer::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(255, 255, 255, 0.4) 50%, 
        transparent 100%);
    transition: left 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
}

/* 切片层基础样式 - 始终可见，无进入动画 */
.slice-layer {
    opacity: 1;
}

/* 移除所有进入动画延迟 */

/* 移除之前的悬浮动画，使用更稳定的微动画 */
.slice-layer:not(:hover):not(.active) {
    animation: gentleFloat 6s ease-in-out infinite;
}

.slice-layer:nth-child(1):not(:hover):not(.active) { 
    animation-delay: 0s; 
}
.slice-layer:nth-child(2):not(:hover):not(.active) { 
    animation-delay: 1s; 
}
.slice-layer:nth-child(3):not(:hover):not(.active) { 
    animation-delay: 2s; 
}
.slice-layer:nth-child(4):not(:hover):not(.active) { 
    animation-delay: 3s; 
}
.slice-layer:nth-child(5):not(:hover):not(.active) { 
    animation-delay: 4s; 
}
.slice-layer:nth-child(6):not(:hover):not(.active) { 
    animation-delay: 5s; 
}

.slice-layer:hover {
    transform: translateZ(15px) translateY(-8px) scale(1.05);
    box-shadow: 
        0 15px 45px rgba(0, 0, 0, 0.2),
        0 6px 24px rgba(0, 0, 0, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    border: 2px solid rgba(24, 144, 255, 0.6);
}

.slice-layer:hover::before {
    opacity: 1;
}

.slice-layer:hover::after {
    left: 100%;
}

.slice-layer.active {
    border: 3px solid #000000;
    background: linear-gradient(135deg, 
        rgba(0, 0, 0, 0.95) 0%, 
        rgba(30, 30, 30, 0.9) 50%,
        rgba(0, 0, 0, 0.95) 100%);
    box-shadow: 
        0 12px 36px rgba(0, 0, 0, 0.4),
        0 6px 18px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    transform: translateZ(20px) translateY(-10px) scale(1.08);
}

.slice-layer.active::before {
    background: linear-gradient(135deg, 
        rgba(0, 0, 0, 0.3) 0%, 
        rgba(0, 0, 0, 0.1) 50%,
        rgba(0, 0, 0, 0.3) 100%);
    opacity: 1;
}

.slice-layer.switching {
    animation: switchingPulse 0.3s ease-in-out;
}

.slice-layer.active::after {
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(255, 255, 255, 0.6) 50%, 
        transparent 100%);
}

.slice-content {
    text-align: center;
    color: #2c3e50;
    position: relative;
    z-index: 10;
    width: 100%;
    align-items: center;
    justify-content: center;
    padding: 0 16px;
}

.slice-name {
    font-size: 16px;
    font-weight: 700;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none;
    position: relative;
}

.slice-name::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #3498db, #2c3e50);
    border-radius: 1px;
    transition: width 0.3s ease;
}

.slice-layer:hover .slice-name::after,
.slice-layer.active .slice-name::after {
    width: 60%;
}

.slice-layer.active .slice-name {
    background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.slice-layer.active .slice-name::after {
    background: linear-gradient(90deg, #ffffff, #f0f0f0);
}

.slice-warning-icon {
    position: absolute;
    right: 8px;
    top: 1px;
    font-size: 16px;
    color: #ff4d4f;
    animation: pulse 2s infinite;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    filter: drop-shadow(0 0 4px rgba(255, 77, 79, 0.5));
    z-index: 20;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.7;
        transform: scale(1.1);
    }
}

.slice-tooltip {
    position: absolute;
    top: 50%;
    left: calc(100% + 20px);
    transform: translateY(-50%);
    background: linear-gradient(135deg, 
        rgba(0, 0, 0, 0.95) 0%, 
        rgba(30, 30, 30, 0.95) 100%);
    color: white;
    padding: 16px 20px;
    border-radius: 12px;
    font-size: 15px;
    z-index: 1000;
    white-space: nowrap;
    box-shadow: 
        0 16px 48px rgba(0, 0, 0, 0.3),
        0 8px 24px rgba(0, 0, 0, 0.2);
    animation: fadeInRight 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.slice-tooltip::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, 
        rgba(24, 144, 255, 0.1) 0%, 
        rgba(24, 144, 255, 0.05) 100%);
    border-radius: inherit;
    pointer-events: none;
}

.slice-tooltip::after {
    content: '';
    position: absolute;
    top: 50%;
    left: -8px;
    transform: translateY(-50%);
    border: 8px solid transparent;
    border-right-color: rgba(0, 0, 0, 0.95);
    filter: drop-shadow(-2px 0 4px rgba(0, 0, 0, 0.2));
}

.tooltip-title {
    font-weight: 600;
    margin: 0;
    color: #fff;
    font-size: 16px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
    position: relative;
    z-index: 1;
}

.tooltip-info {
    display: none !important;
}

.tooltip-info > div {
    display: none !important;
}

.selected-slice-info {
    margin-top: 12px;
    padding: 12px 16px;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.95) 0%, 
        rgba(248, 250, 252, 0.95) 100%);
    border-radius: 12px;
    text-align: center;
    box-shadow: 
        0 6px 24px rgba(0, 0, 0, 0.08),
        0 3px 12px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(20px);
}

.selected-slice-info h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    position: relative;
}

.selected-slice-info h4::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: 50%;
    transform: translateX(-50%);
    width: 30px;
    height: 2px;
    background: linear-gradient(90deg, #3498db, #2c3e50);
    border-radius: 1px;
}

.slice-details {
    gap: 12px;
    width: 100%; /* 固定宽度 */
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

@keyframes shimmer {
    0% {
        background-position: -1000px 0;
    }
    100% {
        background-position: 1000px 0;
    }
}

@keyframes slideInStack {
    from {
        transform: translateZ(-30px) translateY(20px) scale(0.9);
    }
    to {
        transform: translateZ(0) translateY(0) scale(1);
    }
}

@keyframes floatAnimation {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-8px);
    }
}

@keyframes gentleFloat {
    0%, 100% {
        filter: brightness(1) drop-shadow(0 8px 16px rgba(0, 0, 0, 0.1));
    }
    50% {
        filter: brightness(1.02) drop-shadow(0 12px 24px rgba(0, 0, 0, 0.15));
    }
}

@keyframes switchingPulse {
    0% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(1.02);
        opacity: 0.8;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

/* 第二个map-chart定义已移除 - 样式冗余且冲突 */
.timeline-chart {
    width: 100%;
    height: calc(100% - 80px); /* 固定高度，减去标题区域 */
    min-height: 450px; /* 大幅增加时间线图表高度 */
}

/* 链路可用性样式 - 已删除 */

/* availability样式已删除 */

.network-status-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
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
    gap: 15px;
    font-size: 12px;
}

.detail-item {
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
    height: 70px; /* 固定高度 */
    flex-shrink: 0; /* 防止被压缩 */
    box-sizing: border-box; /* 确保padding包含在高度内 */
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

/* 表格行 - 确保等高并紧挨着，水平排列 */
.table-row {
    margin-bottom: 0; /* 移除表格行底部间距 */
    align-items: stretch;
    gap: 5px;
    /* 移除固定高度，让行自适应内容 */
}

.table-row .el-col {
    padding: 0 !important;
    width: calc(50% - 2.5px); /* 固定宽度，两列均分 */
    height: 100%;
}

.table-row .el-col .table-card {
    width: 100%;
    height: 100%;
}

/* 主要卡片样式 */
.responsive-card .el-card__body {
    height: 100%; /* 占满整个卡片 */
    padding: 20px;
    overflow: hidden; /* 防止溢出，由内部组件处理滚动 */
}

/* 确保chart-container充分利用空间 */
.responsive-card .chart-container {
    height: calc(100% - 80px); /* 固定高度，减去标题区域 */
    overflow: hidden; /* 防止内容溢出 */
}

/* 表格卡片 - 确保与左侧卡片等高 */
.table-card {
    height: 100% !important; /* 与左侧chart-card保持一致 */
    z-index: 1; /* 确保z-index低于浮动窗口 */
}

.table-card .el-card__body {
    height: 100% !important; /* 充满卡片高度 */
    padding: 20px; /* 与左侧卡片保持一致的内边距 */
    overflow: hidden; /* 由内部表格处理滚动 */
}

/* 图表行样式 - 确保切片延迟和链路时延卡片等高 */
.chart-row {
    align-items: stretch; /* 确保子元素等高 */
    min-height: calc(100vh - 140px); /* 占满剩余高度，减去顶部筛选栏 */
    position: relative; /* 为延迟弹窗提供定位上下文 */
    overflow: visible; /* 确保弹窗不被裁剪 */
}

.chart-row .el-col {
    height: 100%; /* 固定高度 */
}

.chart-card {
    height: 100% !important;
}

.chart-card .el-card__body {
    height: 100% !important;
    padding: 20px;
    overflow: auto; /* 允许滚动查看隐藏内容 */
}

/* 地图卡片特殊样式 - 减少内边距让地图占据更多空间 */
.beautify-map-card .el-card__body {
    padding: 8px !important; /* 大幅减少内边距 */
}

/* 地图和切片可视化卡片特殊样式 */
.map-slice-card {
    min-height: 480px; /* 减少20%：600px * 0.8 = 480px */
}

.map-slice-card .el-card__body {
    min-height: 440px; /* 减少20%：550px * 0.8 = 440px */
    padding: 20px 0 20px 20px; /* 只移除右边距，保持其他方向的padding */
}

/* 确保chart-container和timeline-chart都充分利用空间 */
.chart-card .chart-container,
.chart-card .timeline-chart {
    height: calc(100% - 80px); /* 固定高度，减去标题区域 */
    min-height: 360px; /* 减少20%：450px * 0.8 = 360px */
}

.table-container {
    overflow: visible; /* 确保滚动条可见 */
    border: 1px solid #ebeef5;
    border-radius: 8px; /* 增加圆角，更美观 */
    background: #fff;
    height: calc(100% - 80px); /* 固定高度，减去标题区域 */
    margin: 8px; /* 四周添加边距，与卡片边界保持美观距离 */
}

/* 表格卡片间距优化 - 已在上方定义，移除重复项 */

.responsive-table {
    height: 100% !important;
    overflow: visible; /* 确保内部滚动条可见 */
}

/* 强制表格充满整个容器 */
.responsive-table .el-table {
    width: 100% !important;
    height: 100% !important; /* 充满容器 */
    border-radius: 4px;
    overflow: hidden; /* 表格本身不滚动，由表格体滚动 */
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

/* 表格主体 - 充满剩余空间并自动滚动 */
.responsive-table .el-table__body-wrapper {
    height: calc(100% - 40px); /* 固定高度，减去表头高度 */
    overflow-y: scroll !important; /* 强制显示垂直滚动条 */
    overflow-x: hidden !important; /* 隐藏横向滚动 */
    max-height: 300px !important; /* 临时设置较小高度确保滚动 */
    min-height: 200px !important; /* 设置最小高度确保能看到内容 */
}

/* 表格行高固定 */
.responsive-table .el-table .el-table__row {
    height: 50px !important; /* 稍微增加行高以容纳更多内容 */
    min-height: 50px !important;
    max-height: 50px !important; /* 确保行高严格固定 */
}

/* 表格单元格高度固定 */
.responsive-table .el-table .el-table__cell {
    padding: 8px 4px !important; /* 调整padding保持紧凑 */
    vertical-align: middle !important;
    height: 50px !important; /* 与行高保持一致 */
    line-height: 1.4 !important; /* 优化文字行间距 */
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
    width: 12px; /* 进一步增加宽度让滚动条更明显 */
    height: 12px;
}

.responsive-table .el-table__body-wrapper::-webkit-scrollbar-track {
    background: #f5f5f5;
    border-radius: 6px;
    border: 1px solid #e0e0e0; /* 添加边框让轨道更明显 */
}

.responsive-table .el-table__body-wrapper::-webkit-scrollbar-thumb {
    background: #409EFF; /* 使用Element Plus主色调 */
    border-radius: 6px;
    border: 2px solid #f5f5f5; /* 添加白色边框增强对比 */
}

.responsive-table .el-table__body-wrapper::-webkit-scrollbar-thumb:hover {
    background: #337ecc; /* 悬停时更深的蓝色 */
}

/* 图表自适应 - 保留timeline-chart，移除重复的map-chart */
.timeline-chart {
    width: 100%;
    height: calc(100% - 80px); /* 固定高度，减去标题区域 */
    min-height: 400px;
}

/* 切片筛选条响应式 */
.slice-filter-bar {
    margin-bottom: 20px;
}

.filter-content {
    display: flex;
    gap: 20px;
}

/* 响应式断点 */
@media (min-width: 769px) {
    /* 桌面端强制水平布局 */
    .left-component,
    .right-component {
        width: 40% !important;
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
    .table-row {
        align-items: stretch;
        gap: 5px;
    }
    
    .table-row .el-col {
        width: calc(50% - 2.5px); /* 固定宽度 */
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
    }
    
    .card-header {
        padding: 15px;
        margin-bottom: 15px;
    }
    
    .chart-container {
        gap: 10px; /* 减少垂直间距 */
        padding: 5px; /* 减少容器内边距 */
    }
    
    /* 全宽地图组件在移动端的样式 */
    .full-map-component {
        min-height: 300px; /* 移动端减少最小高度 */
    }
    
    .left-component,
    .right-component {
        width: 100% !important; /* 全宽度 */
        margin-bottom: 10px; /* 减少底部间距 */
    }
    
    .slice-visualizer {
        min-height: 300px; /* 增加移动端切片可视化高度 */
        padding: 8px; /* 进一步减少移动端内边距 */
    }
    
    .selected-slice-info {
        margin-top: 15px;
        padding: 15px;
    }
    
    .slice-stack {
        width: 80%;
        height: 75%;
        transform: rotateX(15deg) rotateY(-10deg);
    }
    
    .slice-layer {
        height: 50px;
        border-radius: 12px;
    }
    
    .slice-name {
        font-size: 18px;
        padding: 0 16px;
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
    
    .responsive-card .el-card__body {
        min-height: 400px;
        padding: 15px;
    }
    
    .table-card .el-card__body {
        min-height: 266px;
    }
    
    .responsive-table .el-table__body-wrapper {
        height: calc(5 * 36px) !important;
    }
    
    .responsive-table .el-table .el-table__row {
        height: 36px;
    }
    
    /* 移动端只保留timeline-chart样式 */
    .timeline-chart {
        min-height: 350px; /* 增加移动端时间线图表高度 */
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
        align-items: stretch;
        gap: 3px;
    }
    
    .table-row .el-col {
        margin-bottom: 0;
        width: calc(50% - 1.5px); /* 固定宽度 */
    }
    
    .card-header-title {
        font-size: 16px;
    }
    
    .card-header-desc {
        font-size: 12px;
    }
}

@media (max-width: 480px) {
    .responsive-card .el-card__body {
        min-height: 350px;
        padding: 10px;
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
    }
    
    .responsive-table .el-table__body-wrapper {
        height: calc(6 * 32px) !important;
    }
    
    .responsive-table .el-table .el-table__row {
        height: 32px;
    }
    
    /* 平板端只保留timeline-chart样式 */
    .timeline-chart {
        min-height: 250px;
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

/* 确保容器使用固定布局 */
.card-header {
    height: 60px; /* 固定高度 */
}

.responsive-card .el-card__body > div:last-child {
    height: calc(100% - 60px); /* 固定高度，减去标题高度 */
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
    
    .el-tag.two-line-tag {
        height: auto;
        min-height: 36px;
        padding: 4px 6px;
        align-items: center;
        justify-content: center;
        line-height: 1.1;
    }
}

/* ping探测列表样式 */
.header-content {
    justify-content: space-between;
    align-items: flex-start;
    width: 100%;
}

.header-left {
    width: calc(100% - 120px); /* 固定宽度，减去右侧宽度 */
}

.header-right {
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
    width: 100%; /* 固定宽度 */
}

.ping-list {
    overflow-y: auto;
    padding: 10px 12px; /* 减少内边距 */
    height: 100%;
    min-height: 350px; /* 大幅增加ping列表高度 */
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

/* 地图组件美化样式 */
.beautify-map-card {
    background: linear-gradient(135deg, #ffffff 0%, #fafbfc 50%, #f5f7fa 100%);
    border-radius: 20px !important;
    box-shadow: 
        0 8px 40px 0 rgba(0, 0, 0, 0.08), 
        0 3px 16px 0 rgba(0, 0, 0, 0.04),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.1);
    overflow: visible;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}

.beautify-map-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(0, 0, 0, 0.02) 0%, rgba(0, 0, 0, 0.03) 100%);
    border-radius: 20px;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 0;
}

.beautify-map-card:hover {
    box-shadow: 
        0 12px 48px 0 rgba(0, 0, 0, 0.10), 
        0 4px 20px 0 rgba(0, 0, 0, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    transform: translateY(-6px);
    border-color: rgba(0, 0, 0, 0.15);
}

.beautify-map-card:hover::before {
    opacity: 1;
}

/* 覆盖Element Plus卡片默认的焦点和选中样式 */
.beautify-map-card.el-card:focus,
.beautify-map-card.el-card:focus-within,
.beautify-map-card.el-card:active,
.beautify-map-card.el-card:hover {
    box-shadow: 
        0 12px 48px 0 rgba(0, 0, 0, 0.10), 
        0 4px 20px 0 rgba(0, 0, 0, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
    border-color: rgba(0, 0, 0, 0.15) !important;
    outline: none !important;
}

/* 确保地图卡片的所有状态都保持灰色调 */
.map-slice-card.el-card,
.beautify-map-card.el-card {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.map-slice-card.el-card:hover,
.map-slice-card.el-card:focus,
.map-slice-card.el-card:active {
    box-shadow: 
        0 12px 48px 0 rgba(0, 0, 0, 0.10), 
        0 4px 20px 0 rgba(0, 0, 0, 0.06) !important;
    border-color: rgba(0, 0, 0, 0.15) !important;
}

/* 强制覆盖Element Plus的shadow="hover"效果 */
.el-card.is-hover-shadow:hover,
.el-card[shadow="hover"]:hover,
.chart-card.el-card:hover,
.map-slice-card:hover,
.beautify-map-card:hover,
.responsive-card.chart-card.map-slice-card.beautify-map-card.el-card:hover {
    box-shadow: 
        0 12px 48px 0 rgba(0, 0, 0, 0.10), 
        0 4px 20px 0 rgba(0, 0, 0, 0.06) !important;
    border: 1px solid rgba(0, 0, 0, 0.15) !important;
    background: linear-gradient(135deg, #ffffff 0%, #fafbfc 50%, #f5f7fa 100%) !important;
}

/* 覆盖任何可能的蓝色边框或阴影 */
.el-card:hover,
.el-card:focus,
.el-card:active {
    box-shadow: 
        0 12px 48px 0 rgba(0, 0, 0, 0.10), 
        0 4px 20px 0 rgba(0, 0, 0, 0.06) !important;
    border-color: rgba(0, 0, 0, 0.15) !important;
}

/* 特别针对地图卡片的悬停效果 */
.responsive-card.chart-card.map-slice-card.beautify-map-card {
    transition: all 0.3s ease !important;
}

.responsive-card.chart-card.map-slice-card.beautify-map-card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 
        0 8px 32px 0 rgba(0, 0, 0, 0.12), 
        0 3px 16px 0 rgba(0, 0, 0, 0.08) !important;
    border-color: rgba(0, 0, 0, 0.2) !important;
}

/* 最强优先级覆盖 - 针对Element Plus深层样式 */
:deep(.el-card.is-hover-shadow:hover),
:deep(.el-card[shadow="hover"]:hover),
:deep(.chart-card.el-card:hover),
:deep(.map-slice-card:hover),
:deep(.beautify-map-card:hover) {
    background: linear-gradient(135deg, #ffffff 0%, #fafbfc 50%, #f5f7fa 100%) !important;
    border: 1px solid rgba(0, 0, 0, 0.15) !important;
    box-shadow: 
        0 8px 32px 0 rgba(0, 0, 0, 0.12), 
        0 3px 16px 0 rgba(0, 0, 0, 0.08) !important;
}

/* 覆盖Element Plus的全局蓝色主题 */
.el-card.is-hover-shadow.is-never-shadow {
    box-shadow: none !important;
}

.el-card.is-hover-shadow.is-always-shadow,
.el-card.is-hover-shadow {
    --el-card-border-color: rgba(0, 0, 0, 0.1) !important;
    --el-border-color-light: rgba(0, 0, 0, 0.1) !important;
    --el-color-primary: #666666 !important;
    --el-color-primary-light-3: rgba(0, 0, 0, 0.1) !important;
    --el-color-primary-light-5: rgba(0, 0, 0, 0.08) !important;
    --el-color-primary-light-7: rgba(0, 0, 0, 0.06) !important;
    --el-color-primary-light-8: rgba(0, 0, 0, 0.04) !important;
    --el-color-primary-light-9: rgba(0, 0, 0, 0.02) !important;
}

.beautify-card-header {
    background: linear-gradient(90deg, #ffffff 0%, #f0f7ff 100%);
    border-bottom: 2px solid #e0eaff;
    margin-bottom: 12px;
    padding: 16px 20px 12px 20px;
    border-radius: 16px 16px 0 0;
}

.beautify-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #2a3b5d;
    letter-spacing: 0.5px;
    margin: 0;
    text-shadow: 0 1px 2px rgba(42, 59, 93, 0.1);
}

.beautify-desc {
    font-size: 0.95rem;
    color: #6b7a99;
    margin: 4px 0 0 0;
    font-weight: 400;
}

.beautify-map-chart {
    background: linear-gradient(135deg, #f8fbff 0%, #f0f8ff 50%, #e8f4ff 100%);
    border-radius: 16px;
    box-shadow: 
        0 4px 20px 0 rgba(60, 120, 200, 0.1),
        0 2px 10px 0 rgba(60, 120, 200, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(74, 144, 226, 0.2);
    margin: 0; /* 移除margin，防止超出边界 */
    padding: 8px; /* 减少padding */
    transition: all 0.3s ease;
    overflow: hidden; /* 防止内容超出边界 */
    position: relative;
    width: 100%;
    height: 100%;
    box-sizing: border-box; /* 确保padding包含在总尺寸内 */
}

.beautify-map-chart::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(135deg, #ffffff, #ffffff, #ffffff);
    border-radius: 18px;
    z-index: -1;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.beautify-map-chart:hover {
    box-shadow: 
        0 8px 32px 0 rgba(60, 120, 200, 0.15),
        0 4px 16px 0 rgba(60, 120, 200, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    transform: translateY(-2px);
}

.beautify-map-chart:hover::before {
    opacity: 0.6;
}

/* 地图内容容器美化 */
.beautify-map-card .chart-container {
    background: transparent;
    padding: 0; /* 移除内边距，让地图占据更多空间 */
    overflow: visible; /* 确保浮动按钮不被裁剪 */
}

.beautify-map-card .left-component {
    background: rgba(255, 255, 255, 0.6);
    border-radius: 12px;
    padding: 12px;
    margin-right: 8px;
    box-shadow: 0 1px 8px 0 rgba(60, 120, 200, 0.05);
}

.beautify-map-card .right-component {
    background: transparent;
}

/* 探测列表窗口样式 */
:deep(.ping-list-dialog .el-dialog) {
    z-index: 9999 !important;
    min-width: 720px;
}

:deep(.ping-list-dialog .el-dialog__wrapper) {
    z-index: 9999 !important;
}

:deep(.ping-list-dialog .el-overlay) {
    z-index: 9998 !important;
}

.ping-list {
    overflow-y: auto;
    padding: 8px;
}

.ping-item {
    padding: 12px 16px;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    margin-bottom: 8px;
    background: #fafafa;
    transition: all 0.3s ease;
}

.ping-item:hover {
    background: #f0f0f0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
}

.ping-text {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #333;
    line-height: 1.5;
    word-break: break-all;
}

/* 地图容器美化 */
.beautify-map-card .map-container {
    border-radius: 16px;
    overflow: visible;
    position: relative;
    z-index: 1;
}

/* 美化地图卡片样式已简化，移除多余的map-chart定义 */
</style>
