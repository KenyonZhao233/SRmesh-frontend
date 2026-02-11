import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router';
import Home from '../views/home.vue';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        redirect: () => {
            const token = localStorage.getItem('srmesh_token');
            return token ? '/dashboard' : '/login';
        },
    },
    {
        path: '/login',
        name: 'Login',
        meta: {
            title: '登录',
        },
        component: () => import(/* webpackChunkName: "login" */ '../views/pages/login.vue'),
    },
    {
        path: '/home',
        name: 'Home',
        component: Home,
        children: [
            {
                path: 'dashboard',
                name: 'dashboard',
                alias: '/dashboard',
                meta: {
                    title: '系统首页',
                    requiresAuth: true,
                },
                component: () => import(/* webpackChunkName: "dashboard" */ '../views/dashboard.vue'),
            },
            {
                path: 'monitor-management',
                name: 'monitor-management',
                alias: '/monitor-management',
                meta: { title: '监控管理', requiresAuth: true },
                component: () => import('../views/monitor-management.vue'),
            },
            {
                path: 'telemetry',
                name: 'telemetry',
                alias: '/telemetry',
                meta: { title: '遥测信息', requiresAuth: true },
                component: () => import('../views/telemetry.vue'),
            },
            {
                path: 'fault-handling',
                name: 'fault-handling',
                alias: '/fault-handling',
                meta: { title: '故障处理', requiresAuth: true },
                component: () => import('../views/fault-handling.vue'),
            },
            // 设备管理
            {
                path: 'device-management',
                name: 'device-management',
                meta: { title: '网络设备管理', requiresAuth: true },
                redirect: '/device-management/groups',
                children: [
                    {
                        path: 'groups',
                        name: 'device-groups',
                        alias: '/device-management/groups',
                        meta: { title: '组管理', requiresAuth: true },
                        component: () => import('../views/device-management/groups.vue'),
                    },
                    {
                        path: 'devices',
                        name: 'devices',
                        alias: '/device-management/devices',
                        meta: { title: '设备管理', requiresAuth: true },
                        component: () => import('../views/device-management/devices.vue'),
                    },
                    {
                        path: 'batch-add',
                        name: 'batch-add',
                        alias: '/device-management/batch-add',
                        meta: { title: '批量添加', requiresAuth: true },
                        component: () => import('../views/device-management/batch-add.vue'),
                    },
                    {
                        path: 'task-management',
                        name: 'task-management',
                        alias: '/device-management/task-management',
                        meta: { title: '任务配置', requiresAuth: true },
                        component: () => import('../views/device-management/task-management.vue'),
                    },
                    {
                        path: 'snmp',
                        name: 'snmp-info',
                        alias: '/device-management/snmp',
                        meta: { title: 'SNMP信息', requiresAuth: true },
                        component: () => import('../views/device-management/snmp.vue'),
                    },
                ],
            },
            {
                path: '',
                redirect: 'dashboard',
            },
        ],
    },
    {
        path: '/404',
        meta: {
            title: '找不到页面',
        },
        component: () => import(/* webpackChunkName: "404" */ '../views/pages/404.vue'),
    },
    { path: '/:path(.*)', redirect: '/404' },
];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

router.beforeEach((to, from, next) => {
    NProgress.start();
    const title = to.meta.title;
    if (title) {
        document.title = `${title} | SRmesh`;
    }
    
    // 检查是否需要登录验证
    if (to.meta.requiresAuth) {
        const token = localStorage.getItem('srmesh_token');
        if (!token) {
            next('/login');
            return;
        }
    }
    
    // 如果已登录用户访问登录页，重定向到dashboard
    if (to.path === '/login') {
        const token = localStorage.getItem('srmesh_token');
        if (token) {
            next('/dashboard');
            return;
        }
    }
    
    next();
});

router.afterEach(() => {
    NProgress.done();
});

export default router;