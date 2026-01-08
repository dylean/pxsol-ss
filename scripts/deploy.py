#!/usr/bin/env python3
"""
deploy.py - 首次部署 pxsol-ss 程序

功能：将编译好的 Solana 程序 (.so 文件) 部署到链上

使用前提：
    1. 已运行 `cargo build-sbf` 生成 target/deploy/pxsol_ss.so
    2. 已配置 .env 文件（包含私钥和网络配置）
    3. 钱包有足够的 SOL 余额

用法：
    python deploy.py

输出：
    部署成功后会打印程序的公钥地址
"""

import os
import pathlib
import pxsol

# 加载 .env 文件
def load_env():
    """从 .env 文件加载环境变量"""
    env_path = pathlib.Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

# ============ 配置 ============
# 从环境变量读取私钥
PRIVATE_KEY = os.environ.get('SOLANA_PRIVATE_KEY')
if not PRIVATE_KEY:
    print("❌ 错误: 未设置 SOLANA_PRIVATE_KEY 环境变量")
    print("请在项目根目录创建 .env 文件，参考 .env.example")
    exit(1)

# 从环境变量读取网络配置
NETWORK = os.environ.get('SOLANA_NETWORK', 'localhost')
# ==============================

# 配置网络
if NETWORK == 'devnet':
    pxsol.config.current['rpc']['url'] = 'https://api.devnet.solana.com'
    print("🌐 网络: Devnet")
elif NETWORK == 'mainnet':
    pxsol.config.current['rpc']['url'] = 'https://api.mainnet-beta.solana.com'
    pxsol.config.current['rpc']['qps'] = 2  # 主网 QPS 限制
    print("🌐 网络: Mainnet (主网，真钱！)")
else:
    # 默认使用本地测试网 (localhost:8899)
    print("🌐 网络: Localhost (本地测试网)")

# 启用日志
pxsol.config.current.log = 1

# 创建钱包
try:
    prikey = pxsol.core.PriKey.base58_decode(PRIVATE_KEY)
    wallet = pxsol.wallet.Wallet(prikey)
    print(f"👛 钱包地址: {wallet.pubkey.base58()}")
except Exception as e:
    print(f"❌ 私钥格式错误: {e}")
    exit(1)

# 程序二进制文件路径
program_path = pathlib.Path(__file__).parent.parent / 'target/deploy/pxsol_ss.so'

if not program_path.exists():
    print(f"❌ 错误: 找不到程序文件 {program_path}")
    print("请先运行 `cargo build-sbf` 构建程序")
    exit(1)

# 读取程序二进制数据
program_data = program_path.read_bytes()
print(f"📦 程序大小: {len(program_data)} 字节")

# 部署程序
print("\n🚀 正在部署程序...")
try:
    program_pubkey = wallet.program_deploy(bytearray(program_data))
    print(f"\n✅ 部署成功!")
    print(f"📍 程序地址: {program_pubkey}")
except Exception as e:
    print(f"\n❌ 部署失败: {e}")
    print("\n可能的原因:")
    print("  1. 钱包余额不足（Devnet 可使用 solana airdrop 2 <地址> --url devnet）")
    print("  2. 网络连接问题")
    print("  3. 程序文件损坏")
    exit(1)
