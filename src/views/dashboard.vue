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
              <el-col :xs="22" :sm="22" :md="16" :lg="16" :xl="16">
                <el-card shadow="hover" class="responsive-card chart-card map-slice-card beautify-map-card" style="height:100%;display:flex;flex-direction:column;">
                    <div class="card-header beautify-card-header">
                        <p class="card-header-title beautify-title">切片延迟</p>
                    </div>
                    <div class="chart-container">
                        <!-- 左半部分：切片可视化 -->
                        <div class="left-component">
                            <div class="slice-visualizer">
                                <div class="slice-header" style="display:flex;align-items:center;gap:16px;">
                                    <div>
                                        <h3 style="margin-bottom:0;">切片可视化</h3>
                                        <p style="margin:0;">选择要查看的网络切片</p>
                                    </div>
                                    <el-button type="primary" @click="showPingListPopup = true" size="small" style="margin-left:8px;">当前切片探测列表</el-button>
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
                                            :class="[
                                                'slice-layer', 
                                                { 
                                                    'active': selectedSlice === slice.id,
                                                    'switching': isSliceSwitching && selectedSlice === slice.id
                                                }
                                            ]"
                                            :style="getSliceStyle(index)"
                                            @click="selectSlice(slice.id)"
                                            @mouseenter="hoveredSlice = slice.id"
                                            @mouseleave="hoveredSlice = null"
                                        >
                                            <div class="slice-content">
                                                <div class="slice-name">{{ slice.name }}</div>
                                            </div>
                                            <!-- 警告图标 - 当切片有待处理或处理中的问题时显示 -->
                                            <div 
                                                v-if="hasSliceIssues(slice.name)" 
                                                class="slice-warning-icon"
                                                title="此切片存在待处理或处理中的问题"
                                            >
                                                ⚠️
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
                            <div class="map-container">
                                <v-chart 
                                    class="map-chart beautify-map-chart" 
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
                                    </div>
                                    <div class="floating-description">
                                        {{ viewMode === 'geographic' ? '地理视图' : '拓扑视图' }}
                                    </div>
                                </div>
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
                        style="width: 340px; height: 220px; margin-top: 8px;"
                    />
                    <el-button size="mini" type="text" @click="showDelayPopup = false" style="margin-top:8px;">关闭</el-button>
                </div>
            </transition>
            <el-col :xs="26" :sm="26" :md="8" :lg="8" :xl="8">
                <el-card shadow="hover" class="responsive-card table-card" style="height:100%;display:flex;flex-direction:column;">
                    <div class="card-header beautify-card-header">
                        <p class="card-header-title beautify-title">当前问题</p>
                    </div>
                    <div class="table-container">
                        <el-table 
                            :data="currentIssuesData" 
                            style="width: 100%" 
                            class="responsive-table"
                            @row-click="handleIssueRowClick"
                            :row-style="{ cursor: 'pointer' }"
                        >
                            <el-table-column prop="id" label="问题ID" min-width="60" />
                            <el-table-column prop="type" label="问题类型" min-width="60">
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
                            <el-table-column prop="description" label="问题描述" min-width="80"/>
                            <el-table-column prop="slice" label="所属切片" min-width="60" />
                            <el-table-column prop="location" label="位置" min-width="80">
                                <template #default="scope">
                                    {{ formatLinkName(scope.row.location, scope.row.slice || selectedSlice) }}
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
                const mapEl = document.querySelector('.map-chart');
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
const viewMode = ref('geographic'); // 'geographic' 或 'topology'

// 地图聚焦相关变量
const mapCenter = ref([104, 35]); // 地图中心坐标
const mapZoom = ref(1.5); // 地图缩放级别

// 3D切片可视化相关变量
const selectedSlice = ref('physical-network'); // 默认选择物理网络，使用数据库中的实际名称
const hoveredSlice = ref(null);
const zoomLevel = ref(1);
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
    
    // 2. 切换到地理视图
    viewMode.value = 'geographic';
    
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
            const city1Id = parseInt(locationParts[0]);
            const city2Id = parseInt(locationParts[1]);
            
            // 从当前切片的城市数据中查找坐标
            const currentSliceInfo = selectedSliceInfo.value;
            if (currentSliceInfo && currentSliceInfo.filename) {
                const sliceKey = currentSliceInfo.filename.replace('.json', '');
                const sliceData = allSliceTopologies.value[sliceKey];
                
                if (sliceData && sliceData.cities) {
                    const city1 = sliceData.cities.find(c => c.id === city1Id);
                    const city2 = sliceData.cities.find(c => c.id === city2Id);
                    
                    if (city1 && city2) {
                        // 计算两个城市的中点坐标
                        const centerLng = (city1.coord[0] + city2.coord[0]) / 2;
                        const centerLat = (city1.coord[1] + city2.coord[1]) / 2;
                        
                        // 设置地图中心为链路中点
                        mapCenter.value = [centerLng, centerLat];
                        
                        // 设置适当的缩放级别
                        mapZoom.value = 3;
                        
                        console.log(`聚焦到链路中点: [${centerLng}, ${centerLat}]`);
                    } else {
                        console.warn('未找到城市坐标信息');
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

// 3D切片样式生成
const getSliceStyle = (index) => {
    // 反转索引，让第一个元素（物理网络）显示在最上面
    const reverseIndex = networkSlices.value.length - 1 - index;
    const zOffset = reverseIndex * 12; // 减小Z轴偏移
    const yOffset = -reverseIndex * 5; // 减小Y轴偏移
    const scale = 1 - reverseIndex * 0.008; // 减小缩放差异
    const sliceColor = getSliceColor(index);
    
    return {
        transform: `translateZ(${zOffset}px) translateY(${yOffset}px) scale(${scale})`,
        zIndex: networkSlices.value.length - reverseIndex, // 物理网络有最高的zIndex
        backgroundColor: sliceColor + '20',
        borderColor: sliceColor
    };
};

// 选择切片
const selectSlice = (sliceId) => {
    // 设置切换状态
    isSliceSwitching.value = true;
    
    // 添加平滑过渡效果
    const currentActive = document.querySelector('.slice-layer.active') as HTMLElement;
    if (currentActive) {
        currentActive.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    }
    
    selectedSlice.value = sliceId;
    
    // 等待DOM更新后，为新选中的切片添加过渡效果
    nextTick(() => {
        const newActive = document.querySelector('.slice-layer.active') as HTMLElement;
        if (newActive) {
            newActive.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        }
        
        // 延迟重置切换状态，让动画完成
        setTimeout(() => {
            isSliceSwitching.value = false;
        }, 300);
    });
    
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
        const sourceCity = topo.cities.find(city => String(city.id) === String(sourceId));
        const targetCity = topo.cities.find(city => String(city.id) === String(targetId));
        if (sourceCity && targetCity) {
            return `${sourceCity.name} ↔ ${targetCity.name}`;
        }
    }
    // 如果找不到对应的城市，返回原始ID
    return linkId;
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
    // 计算不同状态的问题数量
    const pendingInterruption = currentIssuesData.value.filter(issue => 
        issue.type === '中断' && issue.status === '待处理'
    ).length;
    
    const pendingDelayDrop = currentIssuesData.value.filter(issue => 
        issue.type === '延迟下降' && issue.status === '待处理'  
    ).length;
    
    const processing = currentIssuesData.value.filter(issue => 
        issue.status === '处理中'
    ).length;
    
    const totalActive = sliceStats.value.active;
    const available = Math.max(0, totalActive - pendingInterruption - pendingDelayDrop - processing);
    
    return {
        available: available,           // 可用
        exception: pendingDelayDrop,    // 异常（待处理的延迟下降）
        unavailable: pendingInterruption, // 不可用（待处理的中断）
        unknown: processing,            // 未知（处理中）
        total: totalActive              // 合计
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

// 检查切片是否有待处理或处理中的问题
const hasSliceIssues = (sliceName: string) => {
    return currentIssuesData.value.some(issue => 
        issue.slice === sliceName && 
        (issue.status === '待处理' || issue.status === '处理中')
    );
};

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
});
    // 确保初始选择第一组的第一个切片
    if (displayedSlices.value.length > 0) {
        selectSlice(displayedSlices.value[0].id);
    }
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
/* 链路时延浮窗样式优化 */
.delay-popup {
    position: absolute;
    min-width: 380px;
    min-height: 260px;
    background: #fff;
    border: 3px solid #409eff;
    box-shadow: 0 10px 40px rgba(0,0,0,0.32);
    border-radius: 14px;
    padding: 22px 28px 18px 28px;
    color: #222;
    font-size: 17px;
    z-index: 10000; /* 进一步提高 z-index，确保在所有元素之上 */
    pointer-events: auto;
    opacity: 1;
    transition: all 0.18s cubic-bezier(.4,0,.2,1);
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

/* 确保页面底部有足够间距 */
.dashboard-container {
    padding-bottom: 0; /* 移除页面底部间距 */
    min-height: calc(100vh - 80px); /* 考虑头部导航高度，剩余空间用于内容 */
    display: flex;
    flex-direction: column;
    gap: 20px; /* 为各行添加间距 */
}

/* 确保表格行能充满剩余空间 */
.dashboard-container .table-row {
    flex: 1; /* 让表格行占用剩余的可用空间 */
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
    align-self: stretch; /* 确保垂直拉伸 */
}

.right-component {
    flex: 0 0 76%; /* 增加右侧宽度到76% */
    display: flex;
    flex-direction: column; /* 改为垂直布局，给地图容器更多空间 */
    width: 76%; /* 增加右侧宽度到76% */
    max-width: 76%; /* 防止宽度超出 */
    height: 100%;
    align-self: stretch; /* 确保垂直拉伸 */
}

/* 表格卡片容器 - 确保充满剩余高度 */
.right-component .el-col:last-child {
    flex: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
}

/* 地图容器占据全部空间 */
.map-container {
    flex: 1;
    position: relative;
    height: 100%;
    width: 100%;
    overflow: visible; /* 确保浮动按钮不被裁剪 */
}

/* 地图图表占据全部空间 */
.map-chart {
    width: 100% !important;
    height: 100% !important;
}

/* 浮动切换按钮样式 */
.floating-view-switcher {
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 100;
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
    display: flex;
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
    display: flex;
    flex-direction: column;
    flex: 1;
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
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    perspective: 2000px;
    perspective-origin: 50% 40%;
    position: relative;
    width: 100%;
    height: 100%;
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
    display: flex;
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
    display: flex;
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
    display: flex;
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
    display: flex;
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

/* 警告图标样式 */
.slice-warning-icon {
    position: absolute;
    right: 8px;
    top: 1px;
    font-size: 16px;
    color: #ff4d4f;
    animation: pulse 2s infinite;
    display: flex;
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
    /* 移除固定高度，让行自适应内容 */
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

/* 表格卡片 - 确保与左侧卡片等高 */
.table-card {
    height: 100% !important; /* 与左侧chart-card保持一致 */
    display: flex;
    flex-direction: column;
    z-index: 1; /* 确保z-index低于浮动窗口 */
}

.table-card .el-card__body {
    display: flex;
    flex-direction: column;
    height: 100% !important; /* 充满卡片高度 */
    flex: 1;
    padding: 20px; /* 与左侧卡片保持一致的内边距 */
    overflow: hidden; /* 卡片体不滚动，由内部表格滚动 */
}

/* 图表行样式 - 确保切片延迟和链路时延卡片等高 */
.chart-row {
    display: flex;
    align-items: stretch; /* 确保子元素等高 */
    flex: 0 0 auto; /* 固定尺寸，不参与剩余空间分配 */
    position: relative; /* 为延迟弹窗提供定位上下文 */
    overflow: visible; /* 确保弹窗不被裁剪 */
}

.chart-row .el-col {
    display: flex;
    flex-direction: column;
}

.chart-card {
    height: 100% !important;
    display: flex;
    flex-direction: column;
}

.chart-card .el-card__body {
    height: 100% !important;
    flex: 1;
    display: flex !important;
    flex-direction: column !important;
    padding: 20px;
    overflow: auto; /* 允许滚动查看隐藏内容 */
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
    overflow: hidden; /* 容器本身不滚动 */
    border: 1px solid #ebeef5;
    border-radius: 8px; /* 增加圆角，更美观 */
    background: #fff;
    display: flex;
    flex-direction: column;
    height: 100%; /* 充满剩余空间 */
    max-height: 500px; /* 限制容器最大高度，确保滚动条生效 */
    margin: 8px; /* 四周添加边距，与卡片边界保持美观距离 */
}

/* 表格卡片间距优化 - 已在上方定义，移除重复项 */

.responsive-table {
    height: 100% !important;
    overflow: hidden; /* 表格容器本身不滚动 */
    flex: 1;
    display: flex;
    flex-direction: column;
}

/* 强制表格充满整个容器 */
.responsive-table .el-table {
    width: 100% !important;
    height: auto !important; /* 改为auto，让高度由内容决定 */
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

/* 表格主体 - 设置固定高度并启用滚动 */
.responsive-table .el-table__body-wrapper {
    height: 300px !important; /* 设置固定高度，确保滚动条生效 */
    max-height: 300px !important; /* 最大高度与固定高度一致 */
    overflow-y: auto !important; /* 垂直滚动 */
    overflow-x: hidden !important; /* 隐藏横向滚动 */
}

/* 表格行高固定 */
.responsive-table .el-table .el-table__row {
    height: 40px !important; /* 固定行高保持紧凑 */
    min-height: 40px !important;
    max-height: 40px !important;
}

/* 表格容器内边距 - 已在上方定义，此处删除重复项 */

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
    
    .el-tag.two-line-tag {
        height: auto;
        min-height: 36px;
        padding: 4px 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.1;
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
    margin: 8px 8px 8px 12px;
    padding: 12px;
    transition: all 0.3s ease;
    overflow: visible;
    position: relative;
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
    padding: 8px 8px 12px 8px;
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
    max-height: 400px;
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

.beautify-map-card .map-chart {
    border-radius: 16px;
    position: relative;
    z-index: 1;
}
</style>
