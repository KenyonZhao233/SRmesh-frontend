<template>
    <div class="login-container">
        <div class="login-box">
            <div class="login-header">
                <div class="logo-container">
                    <div class="logo">
                        <img src="@/assets/img/logo.png" alt="SRmesh Logo" width="60" height="60" />
                    </div>
                </div>
                <h2>SRmesh</h2>
            </div>
            
            <el-form
                ref="loginFormRef"
                :model="loginForm"
                :rules="loginRules"
                class="login-form"
                @keyup.enter="submitForm"
            >
                <el-form-item prop="username">
                    <el-input
                        v-model="loginForm.username"
                        placeholder="用户名"
                        size="large"
                        prefix-icon="User"
                    />
                </el-form-item>
                
                <el-form-item prop="password">
                    <el-input
                        v-model="loginForm.password"
                        type="password"
                        placeholder="密码"
                        size="large"
                        prefix-icon="Lock"
                        show-password
                    />
                </el-form-item>
                
                <el-form-item>
                    <el-button
                        type="primary"
                        size="large"
                        :loading="loading"
                        @click="submitForm"
                        class="login-button"
                    >
                        {{ loading ? '登录中...' : '登录' }}
                    </el-button>
                </el-form-item>
            </el-form>
            
            <div class="login-tips">
                <p>演示账号：admin / admin</p>
                <p>本系统为SRmesh算法演示项目</p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, FormInstance, FormRules } from 'element-plus';

const router = useRouter();
const loginFormRef = ref<FormInstance>();
const loading = ref(false);

const loginForm = reactive({
    username: 'admin',
    password: 'admin'
});

const loginRules: FormRules = {
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
    ]
};

const submitForm = async () => {
    if (!loginFormRef.value) return;
    
    try {
        await loginFormRef.value.validate();
        loading.value = true;
        
        // 模拟登录验证
        setTimeout(() => {
            if (loginForm.username === 'admin' && loginForm.password === 'admin') {
                localStorage.setItem('srmesh_token', 'demo_token_' + Date.now());
                ElMessage.success('登录成功');
                router.push('/dashboard');
            } else {
                ElMessage.error('用户名或密码错误');
            }
            loading.value = false;
        }, 1000);
        
    } catch (error) {
        console.error('表单验证失败:', error);
    }
};
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
    width: 400px;
    padding: 40px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.login-header {
    text-align: center;
    margin-bottom: 30px;
}

.logo-container {
    margin-bottom: 20px;
}

.logo {
    display: inline-block;
    animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
}

.login-header h2 {
    color: #2c3e50;
    margin-bottom: 10px;
    font-weight: 600;
    font-size: 28px;
}

.subtitle {
    color: #7f8c8d;
    margin: 0;
    font-size: 14px;
    font-weight: 400;
}

.login-form {
    margin-bottom: 20px;
}

.login-button {
    width: 100%;
}

.login-tips {
    text-align: center;
    font-size: 12px;
    color: #95a5a6;
}

.login-tips p {
    margin: 5px 0;
}
</style>
