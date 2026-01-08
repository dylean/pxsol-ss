#!/usr/bin/env python3
"""
read_data.py - 从链上读取数据

功能：读取用户 PDA 账户中存储的数据

使用前提：
    1. 程序已部署
    2. 本地验证器正在运行
    3. 用户已经写入过数据

用法：
    python read_data.py

注意：
    读取数据不需要签名，也不消耗 SOL
"""

import base64
import pxsol

# 启用日志
pxsol.config.current.log = 1

# ============ 配置区域 ============
# 程序地址（部署时获得，需要根据实际情况修改）
PROGRAM_PUBKEY = 'DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E'
# ==================================

# 创建钱包（用于计算 PDA 地址）
ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def load(user: pxsol.wallet.Wallet) -> bytearray:
    """
    从链上读取用户存储的数据

    Args:
        user: 用户钱包（用于计算 PDA 地址）

    Returns:
        存储的数据（字节数组）

    Raises:
        Exception: 如果数据账户不存在
    """
    prog_pubkey = pxsol.core.PubKey.base58_decode(PROGRAM_PUBKEY)

    # 计算用户的 PDA 数据账户地址
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    print(f"数据账户地址: {data_pubkey.base58()}")

    # 获取账户信息
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})

    if info is None:
        raise Exception("数据账户不存在，请先使用 write_data.py 写入数据")

    # 解码数据
    data = base64.b64decode(info['data'][0])

    return bytearray(data)


if __name__ == '__main__':
    try:
        data = load(ada)
        print(f"\n✅ 读取成功!")
        print(f"数据内容: {data.decode()}")
        print(f"数据大小: {len(data)} 字节")
    except Exception as e:
        print(f"\n❌ 读取失败: {e}")
