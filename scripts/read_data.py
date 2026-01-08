#!/usr/bin/env python3
"""
read_data.py - 从链上读取数据

功能：读取用户 PDA 账户中存储的数据

使用前提：
    1. 程序已部署
    2. 已配置 .env 文件
    3. 用户已经写入过数据

用法：
    python read_data.py

注意：
    读取数据不需要签名，也不消耗 SOL
"""

import base64
import pxsol
import config

# 初始化配置
config.init()

# 获取钱包（用于计算 PDA 地址）
wallet = config.get_wallet()

print(f"📍 程序地址: {config.PROGRAM_PUBKEY}")


def load(user: pxsol.wallet.Wallet) -> bytearray:
    """
    从链上读取用户存储的数据

    Args:
        user: 用户钱包（用于计算 PDA 地址）

    Returns:
        存储的数据（字节数组）
    """
    prog_pubkey = pxsol.core.PubKey.base58_decode(config.PROGRAM_PUBKEY)

    # 计算用户的 PDA 数据账户地址
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    print(f"📦 数据账户地址: {data_pubkey.base58()}")

    # 获取账户信息
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})

    if info is None:
        raise Exception("数据账户不存在，请先使用 write_data.py 写入数据")

    # 解码数据
    data = base64.b64decode(info['data'][0])

    return bytearray(data)


if __name__ == '__main__':
    try:
        data = load(wallet)
        print(f"\n✅ 读取成功!")
        print(f"数据内容: {data.decode()}")
        print(f"数据大小: {len(data)} 字节")
    except Exception as e:
        print(f"\n❌ 读取失败: {e}")
