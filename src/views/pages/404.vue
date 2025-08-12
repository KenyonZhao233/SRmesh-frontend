<template>
    <div class="error-page">
        <div class="error-content">
            <div class="error-code">404</div>
            <div class="error-message">页面未找到</div>
            <div class="error-description">
                抱歉，您访问的页面不存在或已被移除
            </div>
            <div class="error-actions">
                <el-button type="primary" @click="goHome">
                    返回首页
                </el-button>
                <el-button @click="goBack">
                    返回上页
                </el-button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goHome = () => {
    router.push('/dashboard');
};

const goBack = () => {
    router.go(-1);
};
</script>

<style scoped>
.error-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: #f5f5f5;
}

.error-content {
    text-align: center;
    padding: 60px 40px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.error-code {
    font-size: 120px;
    font-weight: bold;
    color: #e74c3c;
    margin-bottom: 20px;
    line-height: 1;
}

.error-message {
    font-size: 28px;
    color: #2c3e50;
    margin-bottom: 15px;
    font-weight: 600;
}

.error-description {
    font-size: 16px;
    color: #7f8c8d;
    margin-bottom: 40px;
    line-height: 1.5;
}

.error-actions {
    display: flex;
    justify-content: center;
    gap: 15px;
}
</style>
