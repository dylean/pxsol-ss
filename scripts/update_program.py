#!/usr/bin/env python3
"""
update_program.py - 更新已部署的程序

功能：将修改后的程序代码重新部署，覆盖已有程序

使用前提：
    1. 程序已经部署过（有程序地址）
    2. 已运行 `cargo build-sbf` 生成新的 target/deploy/pxsol_ss.so
    3. 本地验证器正在运行
    4. 使用的是与部署时相同的钱包（程序的升级权限持有者）

用法：
    python update_program.py

注意：
    - 需要修改 PROGRAM_PUBKEY 为你的程序地址
    - 只有程序的升级权限持有者才能更新程序
"""

import pathlib
import pxsol

# 启用日志
pxsol.config.current.log = 1

# ============ 配置区域 ============
# 程序地址（部署时获得，需要根据实际情况修改）
PROGRAM_PUBKEY = 'DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E'
# ==================================

# 创建钱包（必须与部署时使用的钱包相同）
ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

# 程序公钥
program_pubkey = pxsol.core.PubKey.base58_decode(PROGRAM_PUBKEY)

# 程序二进制文件路径
program_path = pathlib.Path(__file__).parent.parent / 'target/deploy/pxsol_ss.so'

if not program_path.exists():
    print(f"错误: 找不到程序文件 {program_path}")
    print("请先运行 `cargo build-sbf` 构建程序")
    exit(1)

# 读取程序二进制数据
program_data = program_path.read_bytes()
print(f"程序大小: {len(program_data)} 字节")
print(f"目标程序: {PROGRAM_PUBKEY}")

# 更新程序
print("正在更新程序...")
ada.program_update(program_pubkey, program_data)

print("\n✅ 更新成功!")
