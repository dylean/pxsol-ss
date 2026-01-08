# pxsol-ss Python 脚本

本目录包含 pxsol-ss 程序的 Python 管理脚本。

## 环境要求

- **Python**: >= 3.10 (推荐 3.11)
- **pxsol**: 0.4.2 (注意: 0.5.x 版本有兼容性问题)

## 快速开始

### 1. 创建虚拟环境

```bash
# macOS/Linux
python3.11 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动本地测试网络

```bash
# 在新终端窗口运行
solana-test-validator
```

### 4. 空投测试资金

```bash
solana airdrop 100 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt --url http://127.0.0.1:8899
```

## 脚本说明

| 脚本 | 功能 | 用法 |
|------|------|------|
| `deploy.py` | 首次部署程序 | `python deploy.py` |
| `update_program.py` | 更新已部署的程序 | `python update_program.py` |
| `write_data.py` | 写入/创建数据 | `python write_data.py` |
| `read_data.py` | 读取数据 | `python read_data.py` |
| `update_data.py` | 更新数据 | `python update_data.py` |

## 脚本详解

### deploy.py - 部署程序

首次将编译好的 Solana 程序部署到链上。

```bash
# 先构建程序
cargo build-sbf

# 部署
python deploy.py
```

输出示例:
```
"A5S8R7wkjhUoANf2AvNyYSMUxY5wse46VkYEo3Go4pE2"
```

### update_program.py - 更新程序

修改代码后重新部署（覆盖已有程序）。

```bash
# 重新构建
cargo build-sbf

# 更新
python update_program.py
```

### write_data.py - 写入数据

将数据写入链上存储。

```bash
python write_data.py
```

默认写入: `The quick brown fox jumps over the lazy dog`

### read_data.py - 读取数据

从链上读取已存储的数据。

```bash
python read_data.py
```

输出示例:
```
The quick brown fox jumps over the lazy dog
```

### update_data.py - 更新数据

更新已存储的数据（与 write_data 类似，但用于已有数据）。

## 配置说明

### 切换网络

默认连接本地测试网 (`localhost:8899`)。切换到其他网络：

```python
import pxsol

# 本地测试网（默认）
pxsol.config.current = pxsol.config.Config.localhost()

# 开发网
pxsol.config.current = pxsol.config.Config.devnet()

# 主网
pxsol.config.current = pxsol.config.Config.mainnet()
```

### 使用自定义钱包

脚本默认使用测试私钥 `0x01`。使用自定义钱包：

```python
import pxsol

# 从私钥创建
prikey = pxsol.core.PriKey.base58_decode("你的私钥Base58编码")
wallet = pxsol.wallet.Wallet(prikey)

# 生成新钱包
new_wallet = pxsol.wallet.Wallet(pxsol.core.PriKey.generate())
print(f"公钥: {new_wallet.pubkey.base58()}")
print(f"私钥: {new_wallet.prikey.base58()}")
```

## 测试钱包信息

| 属性 | 值 |
|------|-----|
| 私钥 (int) | `0x01` |
| 公钥 | `6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt` |

## 常见问题

### Q: 提示 "Connection refused"

A: 本地验证器未运行。请先执行：
```bash
solana-test-validator
```

### Q: 提示 "AccountNotFound"

A: 钱包余额不足。请先空投：
```bash
solana airdrop 100 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt --url http://127.0.0.1:8899
```

### Q: 提示 "SyntaxError: invalid syntax" 在 match 语句

A: Python 版本过低。请使用 Python 3.10+：
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Q: 提示 "NameError: name 'Pt' is not defined"

A: pxsol 版本问题。请降级到 0.4.2：
```bash
pip install pxsol==0.4.2 --force-reinstall
```
