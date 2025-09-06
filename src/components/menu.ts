import { Menus } from '@/types/menu';

export const menuData: Menus[] = [
    {
        id: '0',
        title: '监控大盘',
        index: '/dashboard',
        icon: 'Odometer',
    },
    {
        id: '2',
        title: '监控管理',
        index: '/monitor-management',
        icon: 'TrendCharts',
    },
    {
        id: '3',
        title: '故障处理',
        index: '/fault-handling',
        icon: 'Warning',
    },
    {
        id: '4',
        title: '网络设备管理',
        index: '4',
        icon: 'Setting',
        children: [
            {
                id: '41',
                pid: '4',
                index: '/device-management/groups',
                title: '组管理',
            },
            {
                id: '42',
                pid: '4',
                index: '/device-management/devices',
                title: '设备管理',
            },
            {
                id: '43',
                pid: '4',
                index: '/device-management/batch-add',
                title: '批量添加',
            },
            {
                id: '44',
                pid: '4',
                index: '/device-management/task-management',
                title: '任务配置',
            },
            {
                id: '45',
                pid: '4',
                index: '/device-management/snmp',
                title: 'SNMP信息',
            },
        ],
    },
];
