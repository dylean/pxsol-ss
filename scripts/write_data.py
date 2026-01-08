#!/usr/bin/env python3
"""
write_data.py - 写入数据到链上

功能：调用 pxsol-ss 程序，将数据存储到用户的 PDA 账户中

使用前提：
    1. 程序已部署
    2. 本地验证器正在运行
    3. 钱包有足够的 SOL 余额

用法：
    python write_data.py

自定义数据：
    修改 main 函数中的 save() 调用参数
"""

import base64
import pxsol

# 启用日志
pxsol.config.current.log = 1

# ============ 配置区域 ============
# 程序地址（部署时获得，需要根据实际情况修改）
PROGRAM_PUBKEY = 'DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E'
# ==================================

# 创建钱包
ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def save(user: pxsol.wallet.Wallet, data: bytearray) -> None:
    """
    将数据存储到链上

    Args:
        user: 用户钱包（数据将存储在该用户的 PDA 账户中）
        data: 要存储的数据（字节数组）
    """
    prog_pubkey = pxsol.core.PubKey.base58_decode(PROGRAM_PUBKEY)

    # 计算用户的 PDA 数据账户地址
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    print(f"数据账户地址: {data_pubkey.base58()}")

    # 构建交易请求
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())

    # 添加账户（顺序必须与程序中的解析顺序一致）
    # 账户 0: 用户账户（签名者 + 可写）
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    # 账户 1: 数据账户（可写）
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    # 账户 2: 系统程序
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    # 账户 3: 租金系统变量
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))

    # 设置要存储的数据
    rq.data = data

    # 构建交易
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(
        pxsol.rpc.get_latest_blockhash({})['blockhash']
    )

    # 签名
    tx.sign([user.prikey])

    # 发送交易
    print("正在发送交易...")
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    print(f"交易 ID: {txid}")

    # 等待确认
    pxsol.rpc.wait([txid])

    # 获取交易日志
    r = pxsol.rpc.get_transaction(txid, {})
    print("\n交易日志:")
    for e in r['meta']['logMessages']:
        print(f"  {e}")

    print(f"\n✅ 数据写入成功!")
    print(f"数据内容: {data.decode() if isinstance(data, (bytes, bytearray)) else data}")
    print(f"数据大小: {len(data)} 字节")


if __name__ == '__main__':
    # 示例：存储一段文本
    save(ada, bytearray(b'The quick brown fox jumps over the lazy dog'))
