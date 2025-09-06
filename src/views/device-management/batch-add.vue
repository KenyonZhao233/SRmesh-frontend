<template>
    <div class="batch-add-container">
        <div class="page-header">
            <h2>批量添加设备</h2>
        </div>

        <el-card shadow="hover" class="form-card">
            <div class="card-header">
                <h3>批量添加网络设备</h3>
            </div>
            
            <el-form :model="batchForm" ref="batchFormRef" :rules="batchRules" label-width="120px">
                <el-row :gutter="20">
                    <el-col :span="12">
                        <el-form-item label="选择设备组" prop="groupId">
                            <el-select v-model="batchForm.groupId" placeholder="请选择设备组" style="width: 100%;">
                                <el-option 
                                    v-for="group in deviceGroups" 
                                    :key="group.id"
                                    :label="`${group.name} (${getDeviceTypeName(group.device_type)})`" 
                                    :value="group.id" 
                                />
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="描述信息">
                            <el-input v-model="batchForm.description" placeholder="描述信息（可选）" />
                        </el-form-item>
                    </el-col>
                </el-row>
                
                <el-form-item label="IP地址列表" prop="ipAddressList">
                    <el-input 
                        v-model="batchForm.ipAddressList"
                        type="textarea" 
                        :rows="10"
                        placeholder="请输入IP地址列表，每行一个IP地址，例如：&#10;192.168.1.1&#10;192.168.1.2&#10;192.168.1.3"
                        style="width: 100%;"
                    />
                    <div class="input-hint">
                        <el-icon><InfoFilled /></el-icon>
                        每行输入一个IP地址，系统将自动为每个IP地址生成设备名称
                    </div>
                </el-form-item>

                <!-- IP地址预览 -->
                <el-form-item label="IP地址预览" v-if="parsedIpList.length > 0">
                    <div class="ip-preview">
                        <div class="preview-header">
                            <span>解析到 {{ parsedIpList.length }} 个有效IP地址</span>
                            <el-button size="small" @click="validateAllIps">验证所有IP</el-button>
                        </div>
                        <div class="ip-list">
                            <el-tag 
                                v-for="(ip, index) in parsedIpList" 
                                :key="index"
                                :type="getIpValidationType(ip)"
                                class="ip-tag"
                            >
                                {{ ip }}
                            </el-tag>
                        </div>
                    </div>
                </el-form-item>

                <!-- 设备预览 -->
                <el-form-item label="设备预览" v-if="previewDevices.length > 0">
                    <div class="device-preview">
                        <div class="preview-header">
                            <span>将创建 {{ previewDevices.length }} 个设备</span>
                        </div>
                        <el-table :data="previewDevices" border size="small" max-height="300">
                            <el-table-column prop="name" label="设备名称" />
                            <el-table-column prop="ipAddress" label="IP地址" />
                            <el-table-column prop="groupName" label="设备组" />
                            <el-table-column prop="description" label="描述" />
                        </el-table>
                    </div>
                </el-form-item>

                <el-form-item>
                    <el-button 
                        type="primary" 
                        @click="submitBatchAdd" 
                        :loading="submitting"
                        :disabled="!previewDevices.length"
                    >
                        <el-icon><Plus /></el-icon>
                        批量添加设备
                    </el-button>
                    <el-button @click="resetForm">重置</el-button>
                </el-form-item>
            </el-form>
        </el-card>

        <!-- 添加结果 -->
        <el-card shadow="hover" class="result-card" v-if="addResults.length > 0">
            <div class="card-header">
                <h3>添加结果</h3>
                <div class="result-summary">
                    <el-tag type="success">成功: {{ successCount }}</el-tag>
                    <el-tag type="danger" style="margin-left: 10px;">失败: {{ failureCount }}</el-tag>
                </div>
            </div>
            
            <el-table :data="addResults" border>
                <el-table-column prop="ipAddress" label="IP地址" />
                <el-table-column prop="deviceName" label="设备名称" />
                <el-table-column prop="status" label="状态" width="100">
                    <template #default="scope">
                        <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                            {{ scope.row.status === 'success' ? '成功' : '失败' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="message" label="消息" />
            </el-table>
        </el-card>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus, InfoFilled } from '@element-plus/icons-vue';

// 表单数据
const batchForm = ref({
    groupId: '',
    ipAddressList: '',
    description: ''
});

// 表单验证规则
const batchRules = {
    groupId: [
        { required: true, message: '请选择设备组', trigger: 'change' }
    ],
    ipAddressList: [
        { required: true, message: '请输入IP地址列表', trigger: 'blur' }
    ]
};

// 状态管理
const submitting = ref(false);
const deviceGroups = ref([]);
const addResults = ref([]);
const ipValidationResults = ref({});

// 计算属性
const parsedIpList = computed(() => {
    if (!batchForm.value.ipAddressList) return [];
    
    return batchForm.value.ipAddressList
        .split('\n')
        .map(ip => ip.trim())
        .filter(ip => ip && ip.length > 0)
        .filter((ip, index, arr) => arr.indexOf(ip) === index); // 去重
});

const previewDevices = computed(() => {
    if (!batchForm.value.groupId || !parsedIpList.value.length) return [];
    
    const selectedGroup = deviceGroups.value.find(g => g.id === batchForm.value.groupId);
    if (!selectedGroup) return [];
    
    return parsedIpList.value
        .filter(ip => isValidIpAddress(ip))
        .map((ip, index) => ({
            name: generateDeviceName(selectedGroup.device_type, ip, index),
            ipAddress: ip,
            groupName: selectedGroup.name,
            description: batchForm.value.description || `批量添加的${getDeviceTypeName(selectedGroup.device_type)}`
        }));
});

const successCount = computed(() => addResults.value.filter(r => r.status === 'success').length);
const failureCount = computed(() => addResults.value.filter(r => r.status === 'failure').length);

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

const isValidIpAddress = (ip) => {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
};

const getIpValidationType = (ip) => {
    if (isValidIpAddress(ip)) {
        return 'success';
    } else {
        return 'danger';
    }
};

const generateDeviceName = (deviceType, ip, index) => {
    const typePrefix = {
        'Cisco': 'CSC',
        'Huawei': 'HW',
        'Juniper': 'JNP',
        'H3C': 'H3C',
        'Ruijie': 'RJ',
        'Other': 'DEV'
    };
    
    const prefix = typePrefix[deviceType] || 'DEV';
    const suffix = ip.split('.').join('');
    return `${prefix}-${suffix}`;
};

const validateAllIps = () => {
    const results = {};
    parsedIpList.value.forEach(ip => {
        results[ip] = isValidIpAddress(ip);
    });
    ipValidationResults.value = results;
    
    const validCount = Object.values(results).filter(Boolean).length;
    const invalidCount = parsedIpList.value.length - validCount;
    
    if (invalidCount === 0) {
        ElMessage.success(`所有 ${validCount} 个IP地址格式正确`);
    } else {
        ElMessage.warning(`发现 ${invalidCount} 个无效IP地址，请检查格式`);
    }
};

const generateSampleIps = () => {
    // 功能已移除
};

const submitBatchAdd = async () => {
    if (!previewDevices.value.length) {
        ElMessage.warning('没有有效的设备可以添加');
        return;
    }
    
    submitting.value = true;
    addResults.value = [];
    
    try {
        // 准备批量添加的设备数据
        const devicesData = previewDevices.value.map(device => ({
            name: device.name,
            ip_address: device.ipAddress,
            group_id: batchForm.value.groupId,
            description: device.description
        }));
        
        // 调用API批量添加设备
        const response = await fetch('http://localhost:3001/api/devices/batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ devices: devicesData })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // 成功添加所有设备
            addResults.value = previewDevices.value.map(device => ({
                ipAddress: device.ipAddress,
                deviceName: device.name,
                status: 'success',
                message: '添加成功'
            }));
            
            ElMessage.success(`批量添加完成，成功添加 ${result.added_count} 个设备`);
        } else {
            // 添加失败
            addResults.value = previewDevices.value.map(device => ({
                ipAddress: device.ipAddress,
                deviceName: device.name,
                status: 'failure',
                message: result.error || '添加失败'
            }));
            
            ElMessage.error(result.error || '批量添加失败');
        }
        
    } catch (error) {
        console.error('批量添加错误:', error);
        ElMessage.error('网络错误，批量添加失败');
        
        // 设置所有设备为失败状态
        addResults.value = previewDevices.value.map(device => ({
            ipAddress: device.ipAddress,
            deviceName: device.name,
            status: 'failure',
            message: '网络连接失败'
        }));
    } finally {
        submitting.value = false;
    }
};

const resetForm = () => {
    batchForm.value = {
        groupId: '',
        ipAddressList: '',
        description: ''
    };
    addResults.value = [];
    ipValidationResults.value = {};
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
        
        // 使用备用数据
        deviceGroups.value = [
            { id: 1, name: '核心路由组', device_type: 'Cisco' },
            { id: 2, name: '接入交换组', device_type: 'Huawei' },
            { id: 3, name: '安全防护组', device_type: 'Cisco' },
            { id: 4, name: '服务器组', device_type: 'H3C' }
        ];
    }
};

// 生命周期
import { onMounted } from 'vue';
onMounted(() => {
    loadDeviceGroups();
});
</script>

<style scoped>
.batch-add-container {
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

.form-card, .result-card {
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

.input-hint {
    margin-top: 5px;
    font-size: 12px;
    color: #909399;
    display: flex;
    align-items: center;
    gap: 5px;
}

.ip-preview, .device-preview {
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

.ip-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.ip-tag {
    margin: 2px;
}

.result-summary {
    display: flex;
    align-items: center;
}
</style>
