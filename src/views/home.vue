<template>
    <div class="layout-container">
        <header class="layout-header">
            <div class="header-content">
                <div class="header-left">
                    <div class="logo-container">
                        <img src="@/assets/img/logo.png" alt="SRmesh Logo" class="header-logo" />
                    </div>
                    <h1 class="system-title">SRmesh</h1>
                </div>
                <div class="header-right">
                    <el-dropdown @command="handleCommand">
                        <span class="user-info">
                            <el-icon><User /></el-icon>
                            Admin
                            <el-icon class="el-icon--right"><arrow-down /></el-icon>
                        </span>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item command="logout">
                                    <el-icon><SwitchButton /></el-icon>
                                    退出登录
                                </el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </div>
            </div>
        </header>
        
        <main class="layout-main">
            <router-view />
        </main>
    </div>
</template>

<script setup lang="ts">
import { User, ArrowDown, SwitchButton } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';

const router = useRouter();

const handleCommand = (command: string) => {
    if (command === 'logout') {
        localStorage.removeItem('srmesh_token');
        ElMessage.success('退出登录成功');
        router.push('/login');
    }
};
</script>

<style scoped>
.layout-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
}

.layout-header {
    background: #242f42;
    color: white;
    padding: 0 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 60px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 15px;
}

.logo-container {
    display: flex;
    align-items: center;
}

.header-logo {
    width: 40px;
    height: 40px;
    object-fit: contain;
}

.system-title {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
}

.user-info {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.user-info:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

.layout-main {
    flex: 1;
    overflow: auto;
    background: #f5f5f5;
}
</style>
