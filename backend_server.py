#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控管理后端服务
用于处理拓扑文件上传和部署管理
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import yaml
import threading
import time
import uuid
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json', 'yaml', 'yml'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 全局变量存储部署任务
deployment_tasks = {}
deployment_logs = {}

class DeploymentManager:
    """部署管理器"""
    
    def __init__(self):
        self.tasks = {}
        
    def create_task(self, task_id, config_file_path):
        """创建部署任务"""
        task = {
            'id': task_id,
            'status': 'pending',
            'config_file': config_file_path,
            'current_step': 0,
            'steps': [
                {
                    'title': '配置验证',
                    'description': '验证拓扑配置文件格式和内容',
                    'status': 'wait'
                },
                {
                    'title': '环境准备',
                    'description': '准备部署环境和依赖',
                    'status': 'wait'
                },
                {
                    'title': '拓扑部署',
                    'description': '部署网络拓扑结构',
                    'status': 'wait'
                },
                {
                    'title': '服务启动',
                    'description': '启动相关网络服务',
                    'status': 'wait'
                },
                {
                    'title': '连接测试',
                    'description': '测试网络连接和服务状态',
                    'status': 'wait'
                },
                {
                    'title': '部署完成',
                    'description': '部署成功，系统正常运行',
                    'status': 'wait'
                }
            ],
            'logs': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.tasks[task_id] = task
        return task
    
    def get_task(self, task_id):
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def update_task_step(self, task_id, step_index, status, message=None):
        """更新任务步骤状态"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if 0 <= step_index < len(task['steps']):
                task['steps'][step_index]['status'] = status
                task['current_step'] = step_index
                task['updated_at'] = datetime.now().isoformat()
                
                if message:
                    self.add_log(task_id, 'info', message)
                
                return True
        return False
    
    def add_log(self, task_id, log_type, message):
        """添加任务日志"""
        if task_id in self.tasks:
            log_entry = {
                'type': log_type,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self.tasks[task_id]['logs'].append(log_entry)
            return True
        return False
    
    def set_task_status(self, task_id, status):
        """设置任务状态"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = status
            self.tasks[task_id]['updated_at'] = datetime.now().isoformat()
            return True
        return False

# 全局部署管理器
deployment_manager = DeploymentManager()

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_topology_file(file_path):
    """验证拓扑配置文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                data = json.load(f)
            elif file_path.endswith(('.yaml', '.yml')):
                data = yaml.safe_load(f)
            else:
                return False, "不支持的文件格式"
        
        # 基本格式验证
        if not isinstance(data, dict):
            return False, "文件格式错误：根节点必须是对象"
        
        # 检查必要字段
        required_fields = ['nodes', 'links']
        for field in required_fields:
            if field not in data:
                return False, f"缺少必要字段：{field}"
        
        # 验证节点SSH配置
        for node in data.get('nodes', []):
            if 'ssh' not in node:
                return False, f"节点 {node.get('id', '未知')} 缺少SSH配置"
            
            ssh_config = node['ssh']
            required_ssh_fields = ['host', 'port', 'username', 'password']
            for field in required_ssh_fields:
                if field not in ssh_config:
                    return False, f"节点 {node.get('id', '未知')} SSH配置缺少字段：{field}"
        
        return True, "配置文件验证通过"
        
    except json.JSONDecodeError as e:
        return False, f"JSON格式错误：{str(e)}"
    except yaml.YAMLError as e:
        return False, f"YAML格式错误：{str(e)}"
    except Exception as e:
        return False, f"文件读取错误：{str(e)}"

def connect_to_node(node_config):
    """模拟SSH连接到节点"""
    ssh_config = node_config.get('ssh', {})
    node_id = node_config.get('id', 'unknown')
    host = ssh_config.get('host')
    port = ssh_config.get('port', 22)
    username = ssh_config.get('username')
    
    # 模拟SSH连接
    print(f"[模拟SSH] 正在连接到节点 {node_id}")
    print(f"[模拟SSH] 主机: {host}:{port}, 用户: {username}")
    print(f"[模拟SSH] 连接成功！")
    
    return True, f"成功连接到节点 {node_id}"

def install_packages_on_node(node_config):
    """模拟在节点上安装软件包"""
    node_id = node_config.get('id', 'unknown')
    
    # 模拟安装过程
    packages = ['frr', 'bird', 'quagga', 'nettools', 'iproute2']
    
    print(f"[模拟安装] 在节点 {node_id} 上安装网络软件包...")
    for package in packages:
        print(f"[模拟安装] 安装 {package}...")
        time.sleep(0.5)  # 模拟安装时间
        print(f"[模拟安装] {package} 安装完成")
    
    print(f"[模拟安装] 节点 {node_id} 所有软件包安装完成")
    return True, f"节点 {node_id} 软件包安装完成"

def configure_node_routing(node_config):
    """模拟配置节点路由"""
    node_id = node_config.get('id', 'unknown')
    router_id = node_config.get('config', {}).get('router_id')
    loopback = node_config.get('config', {}).get('loopback')
    
    print(f"[模拟配置] 配置节点 {node_id} 路由...")
    print(f"[模拟配置] 设置Router ID: {router_id}")
    print(f"[模拟配置] 设置Loopback: {loopback}")
    print(f"[模拟配置] 启动BGP协议...")
    print(f"[模拟配置] 启动OSPF协议...")
    print(f"[模拟配置] 节点 {node_id} 路由配置完成")
    
    return True, f"节点 {node_id} 路由配置完成"

def generate_slice_json(topology_data, output_dir="public/mock/slice"):
    """根据拓扑数据生成切片JSON文件"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        slices = topology_data.get('slices', [])
        nodes = topology_data.get('nodes', [])
        links = topology_data.get('links', [])
        
        for slice_config in slices:
            slice_id = slice_config.get('id')
            slice_name = slice_config.get('name')
            
            # 生成城市列表
            cities = []
            for node in nodes:
                cities.append({
                    "name": node.get('name', ''),
                    "coord": node.get('location', [0, 0]),
                    "AS": 1,
                    "id": node.get('id')
                })
            
            # 生成链路列表
            slice_links = []
            for link in links:
                source_id = link.get('source')
                target_id = link.get('target')
                
                # 找到源和目标节点的坐标
                source_coord = [0, 0]
                target_coord = [0, 0]
                
                for node in nodes:
                    if node.get('id') == source_id:
                        source_coord = node.get('location', [0, 0])
                    elif node.get('id') == target_id:
                        target_coord = node.get('location', [0, 0])
                
                slice_links.append({
                    "source": source_id,
                    "target": target_id,
                    "sourceCoord": source_coord,
                    "targetCoord": target_coord
                })
            
            # 生成切片JSON - 修正格式，添加type字段
            slice_json = {
                "sliceInfo": {
                    "id": slice_id,
                    "name": slice_name,
                    "type": "Custom",  # 添加type字段
                    "description": slice_config.get('description', '')
                },
                "cities": cities,
                "links": slice_links
            }
            
            # 保存文件
            filename = f"{slice_id}.json"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(slice_json, f, ensure_ascii=False, indent=2)
            
            print(f"[生成文件] 切片配置文件: {filepath}")
            
        return True, f"成功生成 {len(slices)} 个切片配置文件"
        
    except Exception as e:
        return False, f"生成切片配置文件失败: {str(e)}"

def generate_pinglist_json(topology_data, output_dir="public/mock/pinglist"):
    """根据拓扑数据生成fullmesh pinglist JSON文件"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        slices = topology_data.get('slices', [])
        nodes = topology_data.get('nodes', [])
        
        for slice_config in slices:
            slice_id = slice_config.get('id')
            slice_name = slice_config.get('name')
            
            # 收集所有节点的loopback地址
            loopback_ips = []
            for node in nodes:
                loopback = node.get('config', {}).get('loopback', '')
                if loopback:
                    # 提取IP地址（去掉子网掩码）
                    ip = loopback.split('/')[0]
                    loopback_ips.append(ip)
            
            # 生成fullmesh pinglist
            ping_list = []
            ping_id = 1
            
            for i, src_ip in enumerate(loopback_ips):
                for j, dst_ip in enumerate(loopback_ips):
                    if i != j:  # 不ping自己
                        ping_list.append({
                            "id": f"ping_{ping_id:03d}",
                            "src": src_ip,
                            "dst": dst_ip,
                            "interval": "300s",
                            "protocol": "TCP"
                        })
                        ping_id += 1
            
            # 生成pinglist JSON
            pinglist_json = {
                "sliceName": slice_name,
                "pingList": ping_list
            }
            
            # 保存文件
            filename = f"{slice_id}.json"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(pinglist_json, f, ensure_ascii=False, indent=2)
            
            print(f"[生成文件] Pinglist配置文件: {filepath}")
            print(f"[生成文件] 生成了 {len(ping_list)} 个ping配置")
            
        return True, f"成功生成 {len(slices)} 个pinglist配置文件"
        
    except Exception as e:
        return False, f"生成pinglist配置文件失败: {str(e)}"

def update_total_slices_json(topology_data, total_slices_path="public/mock/total_slices.json"):
    """更新total_slices.json文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(total_slices_path), exist_ok=True)
        
        # 读取现有的total_slices.json
        existing_slices = []
        if os.path.exists(total_slices_path):
            try:
                with open(total_slices_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_slices = existing_data.get('slices', [])
            except:
                pass
        
        # 获取拓扑中的切片配置
        new_slices = topology_data.get('slices', [])
        
        # 添加新切片到现有列表中（避免重复）
        existing_ids = {slice_item.get('id') for slice_item in existing_slices}
        
        for slice_config in new_slices:
            slice_id = slice_config.get('id')
            if slice_id not in existing_ids:
                new_slice_item = {
                    "id": slice_id,
                    "name": slice_config.get('name'),
                    "filename": f"{slice_id}.json",
                    "description": slice_config.get('description', '')
                }
                existing_slices.append(new_slice_item)
                existing_ids.add(slice_id)
                print(f"[更新配置] 添加新切片: {slice_config.get('name')}")
        
        # 生成更新后的total_slices.json
        updated_data = {
            "totalSlicesCount": 4096,
            "slices": existing_slices,
            "metadata": {
                "lastUpdate": datetime.now().isoformat(),
                "totalSlices": len(existing_slices)
            }
        }
        
        # 保存文件
        with open(total_slices_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        print(f"[更新配置] 更新total_slices.json，总切片数: {len(existing_slices)}")
        return True, f"成功更新total_slices.json，当前总切片数: {len(existing_slices)}"
        
    except Exception as e:
        return False, f"更新total_slices.json失败: {str(e)}"

def test_connectivity(topology_data):
    """模拟测试网络连通性"""
    nodes = topology_data.get('nodes', [])
    links = topology_data.get('links', [])
    
    print(f"[模拟测试] 开始测试网络连通性...")
    print(f"[模拟测试] 总节点数: {len(nodes)}")
    print(f"[模拟测试] 总链路数: {len(links)}")
    
    # 模拟ping测试
    for link in links:
        source = link.get('source')
        target = link.get('target')
        print(f"[模拟测试] 测试 {source} -> {target} 连通性...")
        time.sleep(0.3)
        print(f"[模拟测试] {source} -> {target} 连通性正常")
    
    print(f"[模拟测试] 所有连通性测试通过")
    return True, "网络连通性测试通过"

def simulate_deployment(task_id, config_file_path):
    """模拟部署过程"""
    try:
        logger.info(f"开始部署任务: {task_id}")
        deployment_manager.set_task_status(task_id, 'running')
        deployment_manager.add_log(task_id, 'info', '开始部署过程')
        
        # 读取拓扑配置
        with open(config_file_path, 'r', encoding='utf-8') as f:
            topology_data = json.load(f)
        
        nodes = topology_data.get('nodes', [])
        steps = deployment_manager.get_task(task_id)['steps']
        
        for i, step in enumerate(steps):
            # 更新当前步骤为进行中
            deployment_manager.update_task_step(task_id, i, 'process', f'开始执行: {step["title"]}')
            
            if i == 0:  # 配置验证
                time.sleep(2)
                is_valid, message = validate_topology_file(config_file_path)
                if not is_valid:
                    deployment_manager.update_task_step(task_id, i, 'error', f'配置验证失败: {message}')
                    deployment_manager.set_task_status(task_id, 'failed')
                    return
                deployment_manager.update_task_step(task_id, i, 'finish', '配置验证通过')
                
            elif i == 1:  # 环境准备
                time.sleep(1)
                deployment_manager.add_log(task_id, 'info', f'发现 {len(nodes)} 个节点需要配置')
                
                # 连接到所有节点
                for node in nodes:
                    success, message = connect_to_node(node)
                    if not success:
                        deployment_manager.update_task_step(task_id, i, 'error', f'连接节点失败: {message}')
                        deployment_manager.set_task_status(task_id, 'failed')
                        return
                    deployment_manager.add_log(task_id, 'info', message)
                    time.sleep(0.5)
                
                deployment_manager.update_task_step(task_id, i, 'finish', '环境准备完成，所有节点连接成功')
                
            elif i == 2:  # 拓扑部署
                time.sleep(1)
                
                # 生成配置文件
                deployment_manager.add_log(task_id, 'info', '正在生成切片配置文件...')
                success, message = generate_slice_json(topology_data)
                if not success:
                    deployment_manager.update_task_step(task_id, i, 'error', f'生成切片配置失败: {message}')
                    deployment_manager.set_task_status(task_id, 'failed')
                    return
                deployment_manager.add_log(task_id, 'info', message)
                
                deployment_manager.add_log(task_id, 'info', '正在生成pinglist配置文件...')
                success, message = generate_pinglist_json(topology_data)
                if not success:
                    deployment_manager.update_task_step(task_id, i, 'error', f'生成pinglist配置失败: {message}')
                    deployment_manager.set_task_status(task_id, 'failed')
                    return
                deployment_manager.add_log(task_id, 'info', message)
                
                deployment_manager.add_log(task_id, 'info', '正在更新total_slices配置...')
                success, message = update_total_slices_json(topology_data)
                if not success:
                    deployment_manager.update_task_step(task_id, i, 'error', f'更新total_slices失败: {message}')
                    deployment_manager.set_task_status(task_id, 'failed')
                    return
                deployment_manager.add_log(task_id, 'info', message)
                
                # 在每个节点安装软件包
                for node in nodes:
                    success, message = install_packages_on_node(node)
                    if not success:
                        deployment_manager.update_task_step(task_id, i, 'error', f'软件安装失败: {message}')
                        deployment_manager.set_task_status(task_id, 'failed')
                        return
                    deployment_manager.add_log(task_id, 'info', message)
                    time.sleep(1)
                
                deployment_manager.update_task_step(task_id, i, 'finish', '拓扑部署完成，配置文件已生成，软件安装成功')
                
            elif i == 3:  # 服务启动
                time.sleep(1)
                
                # 配置每个节点的路由
                for node in nodes:
                    success, message = configure_node_routing(node)
                    if not success:
                        deployment_manager.update_task_step(task_id, i, 'error', f'路由配置失败: {message}')
                        deployment_manager.set_task_status(task_id, 'failed')
                        return
                    deployment_manager.add_log(task_id, 'info', message)
                    time.sleep(0.8)
                
                deployment_manager.update_task_step(task_id, i, 'finish', '网络服务启动成功，所有节点路由配置完成')
                
            elif i == 4:  # 连接测试
                time.sleep(1)
                success, message = test_connectivity(topology_data)
                if not success:
                    deployment_manager.update_task_step(task_id, i, 'error', f'连接测试失败: {message}')
                    deployment_manager.set_task_status(task_id, 'failed')
                    return
                deployment_manager.add_log(task_id, 'info', message)
                deployment_manager.update_task_step(task_id, i, 'finish', '网络连接测试通过')
                
            elif i == 5:  # 部署完成
                time.sleep(1)
                deployment_manager.update_task_step(task_id, i, 'finish', '部署成功完成')
                deployment_manager.add_log(task_id, 'success', f'SR-MESH网络拓扑 "{topology_data.get("topology_name", "未知")}" 部署完成')
        
        deployment_manager.set_task_status(task_id, 'completed')
        deployment_manager.add_log(task_id, 'success', '所有部署步骤已完成')
        logger.info(f"部署任务完成: {task_id}")
        
    except Exception as e:
        logger.error(f"部署任务失败: {task_id}, 错误: {str(e)}")
        deployment_manager.add_log(task_id, 'error', f'部署过程中出现错误: {str(e)}')
        deployment_manager.set_task_status(task_id, 'failed')

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '监控管理后端服务运行正常',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # 保存文件
            file.save(file_path)
            
            # 验证文件
            is_valid, message = validate_topology_file(file_path)
            
            logger.info(f"文件上传成功: {unique_filename}, 验证结果: {message}")
            
            return jsonify({
                'message': '文件上传成功',
                'filename': unique_filename,
                'file_path': file_path,
                'validation': {
                    'is_valid': is_valid,
                    'message': message
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': '不支持的文件类型，请上传 JSON 或 YAML 文件'}), 400
            
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

@app.route('/api/validate', methods=['POST'])
def validate_config():
    """配置文件验证接口"""
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({'error': '缺少文件路径参数'}), 400
        
        file_path = data['file_path']
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        is_valid, message = validate_topology_file(file_path)
        
        return jsonify({
            'is_valid': is_valid,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"配置验证失败: {str(e)}")
        return jsonify({'error': f'配置验证失败: {str(e)}'}), 500

@app.route('/api/deploy', methods=['POST'])
def start_deployment():
    """开始部署接口"""
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({'error': '缺少文件路径参数'}), 400
        
        file_path = data['file_path']
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'error': '配置文件不存在'}), 404
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建部署任务
        task = deployment_manager.create_task(task_id, file_path)
        
        # 启动异步部署进程
        deployment_thread = threading.Thread(
            target=simulate_deployment, 
            args=(task_id, file_path)
        )
        deployment_thread.daemon = True
        deployment_thread.start()
        
        logger.info(f"启动部署任务: {task_id}")
        
        return jsonify({
            'message': '部署任务已启动',
            'task_id': task_id,
            'status': task['status'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"启动部署失败: {str(e)}")
        return jsonify({'error': f'启动部署失败: {str(e)}'}), 500

@app.route('/api/deployment/<task_id>', methods=['GET'])
def get_deployment_status(task_id):
    """获取部署状态接口"""
    try:
        task = deployment_manager.get_task(task_id)
        if not task:
            return jsonify({'error': '任务不存在'}), 404
        
        return jsonify({
            'task_id': task_id,
            'status': task['status'],
            'current_step': task['current_step'],
            'steps': task['steps'],
            'logs': task['logs'],
            'created_at': task['created_at'],
            'updated_at': task['updated_at']
        })
        
    except Exception as e:
        logger.error(f"获取部署状态失败: {str(e)}")
        return jsonify({'error': f'获取部署状态失败: {str(e)}'}), 500

@app.route('/api/deployments', methods=['GET'])
def list_deployments():
    """获取所有部署任务列表"""
    try:
        tasks = []
        for task_id, task in deployment_manager.tasks.items():
            tasks.append({
                'task_id': task_id,
                'status': task['status'],
                'current_step': task['current_step'],
                'created_at': task['created_at'],
                'updated_at': task['updated_at']
            })
        
        # 按创建时间倒序排列
        tasks.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'tasks': tasks,
            'total': len(tasks),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取部署列表失败: {str(e)}")
        return jsonify({'error': f'获取部署列表失败: {str(e)}'}), 500

@app.route('/api/files', methods=['GET', 'DELETE'])
def handle_files():
    """处理文件相关操作"""
    if request.method == 'GET':
        # 获取文件列表或文件内容
        file_path = request.args.get('path')
        
        if file_path:
            # 返回特定文件内容
            try:
                if not os.path.exists(file_path):
                    return jsonify({'error': '文件不存在'}), 404
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                return jsonify(content)
            except Exception as e:
                logger.error(f"读取文件失败: {str(e)}")
                return jsonify({'error': f'读取文件失败: {str(e)}'}), 500
        else:
            # 返回上传文件列表（保持原有格式以兼容前端）
            try:
                files = []
                upload_dir = app.config['UPLOAD_FOLDER']
                
                if os.path.exists(upload_dir):
                    for filename in os.listdir(upload_dir):
                        file_path = os.path.join(upload_dir, filename)
                        if os.path.isfile(file_path):
                            stat = os.stat(file_path)
                            files.append({
                                'name': filename,  # 前端期望的字段名
                                'path': file_path,  # 前端期望的字段名
                                'filename': filename,
                                'file_path': file_path,
                                'size': stat.st_size,
                                'upload_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                            })
                
                # 按修改时间倒序排列
                files.sort(key=lambda x: x['modified_at'], reverse=True)
                
                return jsonify(files)  # 直接返回数组以兼容前端
                
            except Exception as e:
                logger.error(f"获取文件列表失败: {str(e)}")
                return jsonify({'error': f'获取文件列表失败: {str(e)}'}), 500
    
    elif request.method == 'DELETE':
        # 删除文件
        file_path = request.args.get('path')
        
        if not file_path:
            return jsonify({'error': '缺少文件路径参数'}), 400
        
        try:
            if not os.path.exists(file_path):
                return jsonify({'error': '文件不存在'}), 404
            
            # 先读取文件内容以获取相关信息
            topology_data = None
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    topology_data = json.load(f)
            except:
                pass
            
            # 删除主文件
            os.remove(file_path)
            logger.info(f"已删除主文件: {file_path}")
            
            # 如果成功读取了拓扑数据，则清理相关生成的文件
            if topology_data:
                try:
                    # 删除生成的slice文件
                    slices = topology_data.get('slices', [])
                    for slice_config in slices:
                        slice_id = slice_config.get('id')
                        slice_file = f"public/mock/slice/{slice_id}.json"
                        pinglist_file = f"public/mock/pinglist/{slice_id}.json"
                        
                        if os.path.exists(slice_file):
                            os.remove(slice_file)
                            logger.info(f"已删除切片文件: {slice_file}")
                        
                        if os.path.exists(pinglist_file):
                            os.remove(pinglist_file)
                            logger.info(f"已删除pinglist文件: {pinglist_file}")
                    
                    # 从total_slices.json中移除相关切片
                    total_slices_path = "public/mock/total_slices.json"
                    if os.path.exists(total_slices_path):
                        with open(total_slices_path, 'r', encoding='utf-8') as f:
                            total_data = json.load(f)
                        
                        existing_slices = total_data.get('slices', [])
                        slice_ids = [s.get('id') for s in slices]
                        updated_slices = [s for s in existing_slices if s.get('id') not in slice_ids]
                        
                        total_data['slices'] = updated_slices
                        total_data['metadata']['totalSlices'] = len(updated_slices)
                        total_data['metadata']['lastUpdate'] = datetime.now().isoformat()
                        
                        with open(total_slices_path, 'w', encoding='utf-8') as f:
                            json.dump(total_data, f, ensure_ascii=False, indent=2)
                        
                        logger.info(f"已从total_slices.json中移除 {len(slice_ids)} 个切片")
                    
                except Exception as cleanup_error:
                    logger.warning(f"清理相关文件时出错: {str(cleanup_error)}")
            
            return jsonify({'message': '文件删除成功'})
            
        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}")
            return jsonify({'error': f'删除文件失败: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件大小超过限制（最大16MB）'}), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    logger.error(f"内部服务器错误: {str(e)}")
    return jsonify({'error': '内部服务器错误'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("监控管理后端服务启动")
    print("服务地址: http://localhost:5000")
    print("上传目录:", os.path.abspath(UPLOAD_FOLDER))
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
