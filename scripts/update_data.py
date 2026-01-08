#!/usr/bin/env python3
"""
update_data.py - 更新链上数据

功能：更新用户 PDA 账户中已存储的数据

使用前提：
    1. 程序已部署
    2. 本地验证器正在运行
    3. 用户已经写入过数据
    4. 钱包有足够的 SOL 余额（如果数据变大需要补充租金）

用法：
    python update_data.py

注意：
    - 更新数据与写入数据使用相同的逻辑
    - 如果新数据比旧数据大，会自动从钱包扣除额外的租金
    - 如果新数据比旧数据小，会自动退还多余的 SOL
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


def update(user: pxsol.wallet.Wallet, new_data: bytearray) -> None:
    """
    更新链上存储的数据

    Args:
        user: 用户钱包
        new_data: 新的数据内容

    说明：
        程序会自动处理：
        - 如果数据变大：从用户账户扣除额外租金
        - 如果数据变小：退还多余的 SOL 到用户账户
        - 重新分配存储空间
    """
    prog_pubkey = pxsol.core.PubKey.base58_decode(PROGRAM_PUBKEY)

    # 计算用户的 PDA 数据账户地址
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    print(f"数据账户地址: {data_pubkey.base58()}")

    # 先读取旧数据，显示对比
    try:
        old_info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
        if old_info:
            old_data = base64.b64decode(old_info['data'][0])
            print(f"旧数据: {old_data.decode()}")
            print(f"旧大小: {len(old_data)} 字节")
    except Exception:
        print("（首次写入，无旧数据）")

    print(f"新数据: {new_data.decode() if isinstance(new_data, (bytes, bytearray)) else new_data}")
    print(f"新大小: {len(new_data)} 字节")

    # 构建交易请求
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())

    # 添加账户
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))  # 用户账户
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))  # 数据账户
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))

    # 设置新数据
    rq.data = new_data

    # 构建交易
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(
        pxsol.rpc.get_latest_blockhash({})['blockhash']
    )

    # 签名
    tx.sign([user.prikey])

    # 发送交易
    print("\n正在发送交易...")
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    print(f"交易 ID: {txid}")

    # 等待确认
    pxsol.rpc.wait([txid])

    # 获取交易日志
    r = pxsol.rpc.get_transaction(txid, {})
    print("\n交易日志:")
    for e in r['meta']['logMessages']:
        print(f"  {e}")

    print(f"\n✅ 数据更新成功!")


if __name__ == '__main__':
    # 示例：更新为新的内容
    update(ada, bytearray(b'Hello, Solana! This is updated data.'))
