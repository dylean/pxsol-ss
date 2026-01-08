#!/usr/bin/env python3
"""
update_program.py - 更新已部署的程序

功能：将修改后的程序代码重新部署，覆盖已有程序

使用前提：
    1. 程序已经部署过
    2. 已运行 `cargo build-sbf` 生成新的 .so 文件
    3. 已配置 .env 文件
    4. 使用的是与部署时相同的钱包

用法：
    python update_program.py
"""

import pathlib
import pxsol
import config

# 初始化配置
config.init()

# 获取钱包（必须与部署时相同）
wallet = config.get_wallet()

# 程序公钥
program_pubkey = pxsol.core.PubKey.base58_decode(config.PROGRAM_PUBKEY)
print(f"📍 目标程序: {config.PROGRAM_PUBKEY}")

# 程序二进制文件路径
program_path = config.PROJECT_ROOT / 'target/deploy/pxsol_ss.so'

if not program_path.exists():
    print(f"❌ 错误: 找不到程序文件 {program_path}")
    print("请先运行 `cargo build-sbf` 构建程序")
    exit(1)

# 读取程序二进制数据
program_data = program_path.read_bytes()
print(f"📦 程序大小: {len(program_data)} 字节")

# 更新程序
print("\n🚀 正在更新程序...")
try:
    wallet.program_update(program_pubkey, program_data)
    print("\n✅ 更新成功!")
except Exception as e:
    print(f"\n❌ 更新失败: {e}")
    exit(1)
