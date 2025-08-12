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
                path: '/dashboard',
                name: 'dashboard',
                meta: {
                    title: '系统首页',
                    requiresAuth: true,
                },
                component: () => import(/* webpackChunkName: "dashboard" */ '../views/dashboard.vue'),
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