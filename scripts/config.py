#!/usr/bin/env python3
"""
config.py - 共享配置模块

从 .env 文件加载配置，供其他脚本使用
"""

import os
import pathlib
import pxsol

# 项目根目录
PROJECT_ROOT = pathlib.Path(__file__).parent.parent

def load_env():
    """从 .env 文件加载环境变量"""
    env_path = PROJECT_ROOT / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

# 加载环境变量
load_env()

# ============ 配置 ============

# 程序地址（Devnet 部署）
PROGRAM_PUBKEY = os.environ.get(
    'SOLANA_PROGRAM_PUBKEY', 
    'GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe'
)

# 私钥
PRIVATE_KEY = os.environ.get('SOLANA_PRIVATE_KEY')

# 网络
NETWORK = os.environ.get('SOLANA_NETWORK', 'localhost')

# ==============================

def setup_network():
    """配置网络连接"""
    if NETWORK == 'devnet':
        pxsol.config.current['rpc']['url'] = 'https://api.devnet.solana.com'
        print("🌐 网络: Devnet")
    elif NETWORK == 'mainnet':
        pxsol.config.current['rpc']['url'] = 'https://api.mainnet-beta.solana.com'
        pxsol.config.current['rpc']['qps'] = 2
        print("🌐 网络: Mainnet")
    else:
        print("🌐 网络: Localhost")

def get_wallet() -> pxsol.wallet.Wallet:
    """获取钱包实例"""
    if not PRIVATE_KEY:
        print("❌ 错误: 未设置 SOLANA_PRIVATE_KEY 环境变量")
        print("请在项目根目录创建 .env 文件，参考 .env.example")
        exit(1)
    
    try:
        prikey = pxsol.core.PriKey.base58_decode(PRIVATE_KEY)
        wallet = pxsol.wallet.Wallet(prikey)
        print(f"👛 钱包地址: {wallet.pubkey.base58()}")
        return wallet
    except Exception as e:
        print(f"❌ 私钥格式错误: {e}")
        exit(1)

def init():
    """初始化配置（设置网络和日志）"""
    setup_network()
    pxsol.config.current['log'] = 1
