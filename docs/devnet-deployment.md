# Devnet 部署与测试记录

> 部署时间: 2026-01-08

本文档记录了 pxsol-ss 程序在 Solana Devnet 上的部署和测试过程。

## 部署信息

| 项目 | 值 |
|------|-----|
| **程序地址** | `GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe` |
| **数据账户 (PDA)** | `HanyYUQEBSWNqJ8wZ1vMeKNwyETJi5YvR1rQBihkF27f` |
| **钱包地址** | `Bt93nvJmvk4KWecAXmER6Y1DpX3eAUsmKo3cm6nZ9Msp` |
| **网络** | Devnet |
| **程序大小** | 75,936 字节 |

### 区块链浏览器链接

- **程序**: https://explorer.solana.com/address/GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe?cluster=devnet
- **数据账户**: https://explorer.solana.com/address/HanyYUQEBSWNqJ8wZ1vMeKNwyETJi5YvR1rQBihkF27f?cluster=devnet
- **钱包**: https://explorer.solana.com/address/Bt93nvJmvk4KWecAXmER6Y1DpX3eAUsmKo3cm6nZ9Msp?cluster=devnet

---

## 部署过程

### 1. 环境准备

```bash
# 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 安装依赖（注意使用 0.4.2 版本）
pip install pxsol==0.4.2
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# Solana 私钥（Base58 格式）
SOLANA_PRIVATE_KEY=你的私钥

# 网络配置
SOLANA_NETWORK=devnet
```

### 3. 空投测试 SOL

```bash
solana airdrop 5 Bt93nvJmvk4KWecAXmER6Y1DpX3eAUsmKo3cm6nZ9Msp --url devnet
```

输出：
```
Requesting airdrop of 5 SOL
Signature: 4peTyzpJBMyxrzvn4xkdybjM2MVpbz3C68qu5Lv7saAxGBVictDvjQPkSm5aPCTNHvqWvREFVuajmNHSWDEFDZ69
10 SOL
```

### 4. 构建程序

```bash
cargo build-sbf
```

### 5. 部署程序

```bash
cd scripts
python deploy.py
```

输出：
```
🌐 网络: Devnet
👛 钱包地址: Bt93nvJmvk4KWecAXmER6Y1DpX3eAUsmKo3cm6nZ9Msp
📦 程序大小: 75936 字节

🚀 正在部署程序...
2026/01/08 12:59:22 pxsol: transaction send signature=4bkesyHSk8VMp7p3a68NVJatJTxtbXxkLNJvk2QnrF1SdoFyRDExm2JibruHHsx6j7ETdaU8gdKCG7eVfB3RuTgi
... (多个交易)
2026/01/08 13:01:02 pxsol: transaction wait unconfirmed=0

✅ 部署成功!
📍 程序地址: "GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe"
```

---

## 功能测试

### 测试 1: 写入数据 (write_data.py)

**命令**：
```bash
python write_data.py
```

**输出**：
```
🌐 网络: Devnet
👛 钱包地址: Bt93nvJmvk4KWecAXmER6Y1DpX3eAUsmKo3cm6nZ9Msp
📍 程序地址: GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe
📦 数据账户地址: HanyYUQEBSWNqJ8wZ1vMeKNwyETJi5YvR1rQBihkF27f

🚀 正在发送交易...
2026/01/08 13:06:06 pxsol: transaction send signature=4GLbaELfNNUtZTcwUXgYdWWCb8qrExfZDAhMuCcPjGiKqxE2jgUnf3FJmo452nhnx8irAbG5tfszpUoDg1PFTyzC
交易 ID: 4GLbaELfNNUtZTcwUXgYdWWCb8qrExfZDAhMuCcPjGiKqxE2jgUnf3FJmo452nhnx8irAbG5tfszpUoDg1PFTyzC
2026/01/08 13:06:07 pxsol: transaction wait unconfirmed=1
2026/01/08 13:06:08 pxsol: transaction wait unconfirmed=0

交易日志:
  Program GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe invoke [1]
  Program 11111111111111111111111111111111 invoke [2]
  Program 11111111111111111111111111111111 success
  Program GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe consumed 7971 of 200000 compute units
  Program GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe success

✅ 数据写入成功!
数据内容: Hello Solana Devnet! This is pxsol-ss storage.
数据大小: 46 字节
```

**结果**: ✅ 通过

**交易链接**: https://explorer.solana.com/tx/4GLbaELfNNUtZTcwUXgYdWWCb8qrExfZDAhMuCcPjGiKqxE2jgUnf3FJmo452nhnx8irAbG5tfszpUoDg1PFTyzC?cluster=devnet

---

### 测试 2: 读取数据 (read_data.py)

**命令**：
```bash
python read_data.py
```

**输出**：
```
🌐 网络: Devnet
👛 钱包地址: Bt93nvJmvk4KWecAXmER6Y1DpX3eAUsmKo3cm6nZ9Msp
📍 程序地址: GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe
📦 数据账户地址: HanyYUQEBSWNqJ8wZ1vMeKNwyETJi5YvR1rQBihkF27f

✅ 读取成功!
数据内容: Hello Solana Devnet! This is pxsol-ss storage.
数据大小: 46 字节
```

**结果**: ✅ 通过

---

### 测试 3: 更新数据 (update_data.py)

**命令**：
```bash
python update_data.py
```

**输出**：
```
🌐 网络: Devnet
👛 钱包地址: Bt93nvJmvk4KWecAXmER6Y1DpX3eAUsmKo3cm6nZ9Msp
📍 程序地址: GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe
📦 数据账户地址: HanyYUQEBSWNqJ8wZ1vMeKNwyETJi5YvR1rQBihkF27f
旧数据: Hello Solana Devnet! This is pxsol-ss storage.
旧大小: 46 字节
新数据: Updated! Hello from Devnet - pxsol-ss works!
新大小: 44 字节

🚀 正在发送交易...
2026/01/08 13:06:20 pxsol: transaction send signature=5wHTr1UbCosCRpuCAyB9JH1N8E3rW2d5WnfjiZAaEH2Sw2ZE48Qyp51xbFqiVrZAEdzkRwdxS1TGhqT9CgJMUhYJ
交易 ID: 5wHTr1UbCosCRpuCAyB9JH1N8E3rW2d5WnfjiZAaEH2Sw2ZE48Qyp51xbFqiVrZAEdzkRwdxS1TGhqT9CgJMUhYJ
2026/01/08 13:06:21 pxsol: transaction wait unconfirmed=1
2026/01/08 13:06:22 pxsol: transaction wait unconfirmed=0

交易日志:
  Program GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe invoke [1]
  Program GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe consumed 5975 of 200000 compute units
  Program GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe success

✅ 数据更新成功!
```

**结果**: ✅ 通过

**交易链接**: https://explorer.solana.com/tx/5wHTr1UbCosCRpuCAyB9JH1N8E3rW2d5WnfjiZAaEH2Sw2ZE48Qyp51xbFqiVrZAEdzkRwdxS1TGhqT9CgJMUhYJ?cluster=devnet

---

### 测试 4: 验证更新后数据

**命令**：
```bash
python read_data.py
```

**输出**：
```
🌐 网络: Devnet
👛 钱包地址: Bt93nvJmvk4KWecAXmER6Y1DpX3eAUsmKo3cm6nZ9Msp
📍 程序地址: GxL6gD17N57d4Ub1Gx2xao16LQd8G7uQE2crtW8bKFNe
📦 数据账户地址: HanyYUQEBSWNqJ8wZ1vMeKNwyETJi5YvR1rQBihkF27f

✅ 读取成功!
数据内容: Updated! Hello from Devnet - pxsol-ss works!
数据大小: 44 字节
```

**结果**: ✅ 通过（数据已正确更新）

---

## 测试总结

| 测试项 | 状态 | 计算单元消耗 |
|--------|------|-------------|
| 部署程序 | ✅ 通过 | - |
| 写入数据 (首次创建) | ✅ 通过 | 7,971 CU |
| 读取数据 | ✅ 通过 | 0 CU (只读) |
| 更新数据 (缩小) | ✅ 通过 | 5,975 CU |
| 验证更新 | ✅ 通过 | 0 CU (只读) |

### 关键观察

1. **首次写入 vs 更新**：
   - 首次写入消耗 7,971 CU（需要调用系统程序创建账户）
   - 更新数据消耗 5,975 CU（直接修改现有账户）

2. **数据大小变化**：
   - 原数据：46 字节
   - 新数据：44 字节（变小）
   - 程序正确处理了空间缩小的情况

3. **PDA 地址**：
   - 数据账户地址 `HanyYUQEBSWNqJ8wZ1vMeKNwyETJi5YvR1rQBihkF27f` 由用户公钥和程序 ID 确定性派生
   - 每次运行都会得到相同的地址

---

## 遇到的问题

### 问题 1: Devnet RPC 不稳定

**现象**：偶尔出现 `Connection reset by peer` 错误

**原因**：Devnet 公共 RPC 端点有时不稳定

**解决**：重试即可，或使用专用 RPC 服务（如 Helius、QuickNode）

### 问题 2: pxsol 版本兼容性

**现象**：pxsol 0.5.x 版本在 Python 3.11+ 上报错

**解决**：使用 pxsol 0.4.2 版本

```bash
pip install pxsol==0.4.2
```

---

## 费用记录

| 操作 | 费用 (SOL) |
|------|-----------|
| 程序部署 | ~2.5 SOL |
| 写入数据 (46 字节) | ~0.001 SOL |
| 更新数据 | ~0.000005 SOL |
| 读取数据 | 0 SOL |

---

## 附录：脚本文件

### 项目结构

```
pxsol-ss/
├── .env                    # 环境变量（私钥、网络配置）
├── .env.example            # 环境变量模板
├── scripts/
│   ├── config.py           # 共享配置模块
│   ├── deploy.py           # 部署程序
│   ├── write_data.py       # 写入数据
│   ├── read_data.py        # 读取数据
│   ├── update_data.py      # 更新数据
│   └── update_program.py   # 更新程序
├── src/
│   └── lib.rs              # Rust 程序源码
└── docs/
    ├── docs.md             # 完整开发文档
    └── devnet-deployment.md # 本文档
```

### 配置模块 (config.py)

共享配置模块从 `.env` 文件加载环境变量，提供统一的配置接口：

- `SOLANA_PRIVATE_KEY`: 私钥（Base58 格式）
- `SOLANA_NETWORK`: 网络（localhost/devnet/mainnet）
- `SOLANA_PROGRAM_PUBKEY`: 程序地址（可选）

---

*文档最后更新: 2026-01-08*
