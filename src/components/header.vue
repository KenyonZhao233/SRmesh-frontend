<template>
    <div class="header">
        <!-- Logo和标题 -->
        <div class="header-left">
            <img class="logo" src="../assets/img/logo.png" alt="" />
            <div class="web-title">SRmesh</div>
        </div>
        <div class="header-right">
            <div class="header-user-con">
                <div class="btn-icon" @click="setFullScreen">
                    <el-tooltip effect="dark" content="全屏" placement="bottom">
                        <i class="el-icon-lx-full"></i>
                    </el-tooltip>
                </div>
                <div class="btn-icon" @click="handleLogout">
                    <el-tooltip effect="dark" content="退出登录" placement="bottom">
                        <i class="el-icon-lx-exit"></i>
                    </el-tooltip>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();

const setFullScreen = () => {
    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else {
        document.body.requestFullscreen.call(document.body);
    }
};

const handleLogout = () => {
    ElMessageBox.confirm('确认退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    }).then(() => {
        localStorage.removeItem('srmesh_token');
        localStorage.removeItem('srmesh_user');
        ElMessage.success('已退出登录');
        router.push('/login');
    }).catch(() => {
        // 用户取消
    });
};
</script>
<style scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-sizing: border-box;
    width: 100%;
    height: 70px;
    color: var(--header-text-color);
    background-color: var(--header-bg-color);
    border-bottom: 1px solid #ddd;
}

.header-left {
    display: flex;
    align-items: center;
    padding-left: 20px;
    height: 100%;
}

.logo {
    width: 35px;
}

.web-title {
    margin: 0 40px 0 10px;
    font-size: 22px;
}

.header-right {
    float: right;
    padding-right: 50px;
}

.header-user-con {
    display: flex;
    height: 70px;
    align-items: center;
}

.btn-icon {
    position: relative;
    width: 30px;
    height: 30px;
    text-align: center;
    cursor: pointer;
    display: flex;
    align-items: center;
    color: var(--header-text-color);
    margin: 0 5px;
    font-size: 20px;
}
</style>
