#!/usr/bin/env python3
"""
deploy.py - 首次部署 pxsol-ss 程序

功能：将编译好的 Solana 程序 (.so 文件) 部署到链上

使用前提：
    1. 已运行 `cargo build-sbf` 生成 target/deploy/pxsol_ss.so
    2. 本地验证器正在运行 (solana-test-validator)
    3. 钱包有足够的 SOL 余额

用法：
    python deploy.py

输出：
    部署成功后会打印程序的公钥地址
"""

import pathlib
import pxsol

# 启用日志，方便调试
pxsol.config.current.log = 1

# 创建钱包（使用测试私钥 0x01）
# 公钥: 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

# 程序二进制文件路径（相对于项目根目录）
program_path = pathlib.Path(__file__).parent.parent / 'target/deploy/pxsol_ss.so'

if not program_path.exists():
    print(f"错误: 找不到程序文件 {program_path}")
    print("请先运行 `cargo build-sbf` 构建程序")
    exit(1)

# 读取程序二进制数据
program_data = program_path.read_bytes()
print(f"程序大小: {len(program_data)} 字节")

# 部署程序
print("正在部署程序...")
program_pubkey = ada.program_deploy(bytearray(program_data))

print(f"\n✅ 部署成功!")
print(f"程序地址: {program_pubkey}")
