<template>
    <div>
        <div class="container">
            <div class="form-box">
                <el-form ref="formRef" :model="form" label-width="120px">
                    <el-form-item label="目标设备选择">
                        <el-input
                            type="textarea"
                            :rows="6"
                            :placeholder="targetsPlaceholder"
                            v-model="form.targets"
                        />
                        <div class="input-hint"><el-icon><InfoFilled /></el-icon> 自动解析下方实时更新（host 与 group 混合输入时，会去重汇总实际执行设备）</div>
                    </el-form-item>

                    <el-form-item label="目标预览">
                        <div class="preview-box">
                            <div class="preview-section">
                                <div class="section-title">目标列表：</div>
                <div class="tag-list">
                                    <el-tag
                                        v-for="(t, idx) in parsedTargets"
                                        :key="idx"
                    :type="t.valid ? (t.type === 'host' ? 'success' : 'warning') : 'danger'"
                                        class="mr6"
                                    >
                                        {{ t.type || 'unknown' }}: {{ t.value }}<span v-if="!t.valid"> (无效)</span>
                                    </el-tag>
                                    <span v-if="parsedTargets.length === 0" class="muted">无</span>
                                </div>
                            </div>
                            <div class="preview-section">
                <div class="section-title">实际执行设备（{{ resolvedDevices.length }}个）：</div>
                                <div class="tag-list">
                                    <el-tag
                                        v-for="d in resolvedDevices"
                                        :key="d.id || d.name"
                                        type="info"
                                        class="mr6"
                                    >
                                        {{ d.name }}
                                    </el-tag>
                                    <span v-if="resolvedDevices.length === 0" class="muted">无匹配设备</span>
                                </div>
                            </div>
                        </div>
                    </el-form-item>

                    <el-form-item label="CLI命令">
                        <el-input 
                            class="cli-input"
                            type="textarea" 
                            :rows="8" 
                            v-model="form.command"
                            :placeholder="commandPlaceholder"
                            spellcheck="false"
                        />
                        <div class="input-hint"><el-icon><InfoFilled /></el-icon> 系统会按行顺序执行命令</div>
                    </el-form-item>

                    <el-form-item>
                        <el-button type="primary" @click="onSubmit" :disabled="!resolvedDevices.length">提交</el-button>
                        <el-button @click="onReset">重置</el-button>
                    </el-form-item>
                </el-form>
            </div>
        </div>
    </div>
    
</template>

<script setup lang="ts" name="task-management">
import { ref, reactive, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { InfoFilled } from '@element-plus/icons-vue';
import type { FormInstance } from 'element-plus';

const formRef = ref<FormInstance>();
const form = reactive({
    targets: '',
    command: '',
});

const targetsPlaceholder = `每行一个目标，支持：
- host:设备名称或IP地址
- group:设备组名称
示例：
host:192.168.1.10
group:Group A`;

const commandPlaceholder = `请输入CLI命令，支持多行。示例：
show version
show ip interface brief
show running-config`;

// 设备与设备组数据（从后端API加载）
type Device = { id: number; name: string; ip_address: string; group_id: number; device_type?: string; group_name?: string };
type Group = { id: number; name: string };

const deviceGroups = ref<Group[]>([]);
const allDevices = ref<Device[]>([]);

// 解析输入的目标
const parsedTargets = computed(() => {
    if (!form.targets) return [] as Array<{ type: string; value: string; valid: boolean; error?: string }>;
    return form.targets
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => {
            // 支持无类型前缀时默认按 host 处理
            if (!line.includes(':')) {
                return { type: 'host', value: line, valid: true };
            }
            const [typeRaw, ...rest] = line.split(':');
            const type = typeRaw.trim().toLowerCase();
            const value = rest.join(':').trim();
            if (!value) return { type, value, valid: false, error: '值为空' };
            if (!['host', 'group'].includes(type)) {
                return { type, value, valid: false, error: '类型必须是 host 或 group' };
            }
            return { type, value, valid: true };
        });
});

// 解析得到的实际执行设备（去重）
const resolvedDevices = computed<Device[]>(() => {
    const out: Device[] = [];
    const addUnique = (d: Device) => {
        if (!out.find(x => x.id === d.id)) out.push(d);
    };
    parsedTargets.value.filter(t => t.valid).forEach(t => {
        if (t.type === 'host') {
            const dev = allDevices.value.find(d => d.name === t.value || d.ip_address === t.value);
            if (dev) addUnique(dev);
        } else if (t.type === 'group') {
            const g = deviceGroups.value.find(g => g.name === t.value);
            if (g) {
                allDevices.value.filter(d => d.group_id === g.id).forEach(addUnique);
            }
        }
    });
    return out;
});

const onSubmit = () => {
    if (!resolvedDevices.value.length) {
        ElMessage.warning('未找到可执行设备');
        return;
    }
    ElMessage.success(`提交成功，将在 ${resolvedDevices.value.length} 台设备上执行`);
};

const onReset = () => {
    formRef.value?.resetFields();
};

// 加载后端数据
import { onMounted } from 'vue';
const loadDeviceGroups = async () => {
    try {
        const res = await fetch('http://localhost:3001/api/device-groups');
        deviceGroups.value = await res.json();
    } catch (e) {
        deviceGroups.value = [];
    }
};
const loadAllDevices = async () => {
    try {
        const res = await fetch('http://localhost:3001/api/devices');
        allDevices.value = await res.json();
    } catch (e) {
        allDevices.value = [];
    }
};
onMounted(() => {
    loadDeviceGroups();
    loadAllDevices();
});
</script>

<style scoped>
.form-box {
    width: 600px;
}
.input-hint {
    margin-top: 6px;
    font-size: 12px;
    color: #666;
    display: flex;
    align-items: center;
}
.input-hint .el-icon { margin-right: 6px; }
.preview-box { border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; background: #fafafa; }
.preview-section { margin-bottom: 10px; }
.section-title { font-weight: 600; margin-bottom: 6px; color: #2c3e50; }
.tag-list { display: flex; flex-wrap: wrap; gap: 6px; }
.mr6 { margin-right: 6px; }
.muted { color: #999; }

/* Terminal-like style for CLI input */
.cli-input :deep(.el-textarea__inner) {
    background: #0b0b0b;
    color: #e6e6e6;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    line-height: 1.5;
    border-color: #2a2a2a;
    box-shadow: none;
    caret-color: #22c55e; /* green caret */
}
.cli-input :deep(.el-textarea__inner::placeholder) {
    color: #8b8b8b;
}
.cli-input :deep(.el-textarea__inner:focus) {
    border-color: #3b82f6;
}
</style>
