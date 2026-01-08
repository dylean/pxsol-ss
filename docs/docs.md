# pxsol-ss 完整开发文档

> Solana 链上数据存储程序 - 从零开始的完整指南

## 目录

1. [项目概述](#项目概述)
2. [环境配置](#环境配置)
3. [遇到的问题与解决方案](#遇到的问题与解决方案)
4. [程序代码详解](#程序代码详解)
5. [构建与部署](#构建与部署)
6. [使用指南](#使用指南)
7. [Web2 vs Solana 概念对照](#web2-vs-solana-概念对照)

---

## 项目概述

### 这是什么？

`pxsol-ss` 是一个部署在 Solana 区块链上的智能合约（程序），提供简单的 **Key-Value 数据存储** 功能。

用 Web2 的话来说，这就是一个 **带自动计费的云存储服务 API**：
- 每个用户有一个专属的存储账户
- 用户可以存储任意字节数据
- 系统自动管理存储费用（存多了收费，存少了退款）
- 所有操作都在链上执行，透明可验证

### 项目结构

```
pxsol-ss/
├── Cargo.toml          # Rust 项目配置文件
├── Cargo.lock          # 依赖锁定文件
├── src/
│   └── lib.rs          # 程序源代码（带详细注释）
├── target/
│   └── deploy/
│       └── pxsol_ss.so # 编译后的程序二进制文件
├── deploy.py           # Python 部署脚本
├── .venv/              # Python 虚拟环境
├── .gitignore
└── docs/
    └── docs.md         # 本文档
```

---

## 环境配置

### 1. 安装 Rust 和 Solana 工具链

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# 验证安装
rustc --version
solana --version
```

### 2. 安装 Solana BPF 工具链

```bash
# 这个命令会自动安装 cargo-build-sbf 等工具
solana-install update
```

### 3. 配置 Python 环境

由于 `pxsol` 库需要 Python 3.10+ 的 `match` 语法支持，需要使用较新版本的 Python：

```bash
# 安装 Python 3.11（macOS 使用 Homebrew）
brew install python@3.11

# 创建虚拟环境
python3.11 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装 pxsol（注意：使用 0.4.2 版本，0.5.4 有 bug）
pip install pxsol==0.4.2
```

---

## 遇到的问题与解决方案

### 问题 1：Rust Edition 2024 不支持

**错误信息：**
```
error: failed to parse manifest at `/Users/dean/code/web3/pxsol-ss/Cargo.toml`

Caused by:
  feature `edition2024` is required
  The package requires the Cargo feature called `edition2024`, but that feature is 
  not stabilized in this version of Cargo (1.84.0)
```

**原因：** `Cargo.toml` 中使用了 `edition = "2024"`，但 Rust 2024 edition 在当前 Cargo 版本中还是不稳定特性。

**解决方案：** 修改 `Cargo.toml`，将 edition 改为稳定版本：

```toml
# 修改前
edition = "2024"

# 修改后
edition = "2021"
```

---

### 问题 2：pxsol 模块找不到

**错误信息：**
```
ModuleNotFoundError: No module named 'pxsol'
```

**解决方案：** 安装 pxsol 模块：

```bash
pip install pxsol
```

---

### 问题 3：Python 3.9 不支持 match 语法

**错误信息：**
```
File ".../pxsol/core.py", line 604
    match k:
          ^
SyntaxError: invalid syntax
```

**原因：** `pxsol` 库使用了 Python 3.10+ 才支持的 `match` 语法，但系统默认 Python 是 3.9。

**解决方案：** 升级到 Python 3.11：

```bash
# macOS
brew install python@3.11

# 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate
```

---

### 问题 4：pxsol 0.5.4 版本有 bug

**错误信息：**
```
File ".../pxsol/ed25519.py", line 117, in Pt
    def __mul__(self, k: Fr) -> Pt:
                                ^^
NameError: name 'Pt' is not defined
```

**原因：** `pxsol 0.5.4` 版本在类型注解中有前向引用问题。

**解决方案：** 降级到 0.4.2 版本：

```bash
pip install pxsol==0.4.2 --force-reinstall
```

---

### 问题 5：本地 Solana 节点未运行

**错误信息：**
```
ConnectionRefusedError: [Errno 61] Connection refused
HTTPConnectionPool(host='127.0.0.1', port=8899): Max retries exceeded
```

**原因：** `deploy.py` 默认连接本地 Solana 节点 (localhost:8899)，但没有运行本地验证器。

**解决方案：** 启动 Solana 本地测试验证器：

```bash
solana-test-validator
```

---

### 问题 6：测试钱包没有 SOL

**错误信息：**
```
Exception: {'code': -32002, 'message': 'Transaction simulation failed: 
Attempt to debit an account but found no record of a prior credit.', 
'data': {'err': 'AccountNotFound', ...}}
```

**原因：** `deploy.py` 使用的测试钱包 (私钥=0x01) 在本地测试网上没有资金。

**解决方案：** 使用 airdrop 命令给钱包空投 SOL：

```bash
# 钱包地址是从私钥 0x01 派生的
solana airdrop 100 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt --url http://127.0.0.1:8899
```

---

## 程序代码详解

### 核心概念

在阅读代码之前，先了解几个 Solana 核心概念：

| 概念 | Web2 类比 | 说明 |
|------|-----------|------|
| **Program** | 后端 API 服务 | 部署在链上的可执行代码 |
| **Account** | 数据库记录 | 链上存储数据的基本单位 |
| **Instruction** | API 请求 | 调用程序的一次操作 |
| **Transaction** | HTTP 请求 | 包含一个或多个 Instruction |
| **Lamports** | 分 (货币) | SOL 的最小单位，1 SOL = 10^9 lamports |
| **Rent** | 存储费 | 账户需要持有足够 SOL 以避免被删除 |
| **PDA** | 托管账户 | 由程序控制的账户，没有私钥 |

### 程序入口

```rust
solana_program::entrypoint!(process_instruction);
```

这行代码声明程序入口点，类似于：
- Java 的 `public static void main()`
- Node.js 的 Express 路由处理器

### 函数签名

```rust
pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,  // 程序自己的地址
    accounts: &[solana_program::account_info::AccountInfo],  // 参与交易的账户
    data: &[u8],  // 用户传入的数据
) -> solana_program::entrypoint::ProgramResult
```

类比 Express.js：

```javascript
app.post('/api/store', (req, res) => {
    const programId = req.baseUrl;      // program_id
    const accounts = req.accounts;       // accounts
    const data = req.body;               // data
});
```

### 账户解析

```rust
let account_user = next_account_info(accounts_iter)?;  // 用户账户
let account_data = next_account_info(accounts_iter)?;  // 数据存储账户
let _ = next_account_info(accounts_iter)?;             // 系统程序
let _ = next_account_info(accounts_iter)?;             // 租金系统变量
```

Solana 的特点：所有参与交易的账户必须预先声明并按顺序传入。

### 计算租金豁免

```rust
let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());
```

Solana 上存储数据需要付费。`rent_exemption` 是存储指定大小数据所需的最小 SOL 余额。

大约费用参考：
- 100 字节 → ~0.00158 SOL
- 1 KB → ~0.00802 SOL
- 10 KB → ~0.07850 SOL

### PDA 地址推导

```rust
let bump_seed = solana_program::pubkey::Pubkey::find_program_address(
    &[&account_user.key.to_bytes()],
    program_id,
).1;
```

**PDA (Program Derived Address)** 是 Solana 的一个重要概念：
- 地址由种子（这里是用户公钥）和程序 ID 确定性派生
- PDA 不在 ed25519 曲线上，**没有对应的私钥**
- 只有程序可以代表 PDA 签名

类比：银行的保管箱，只有银行（程序）能打开，但属于你（用户）。

### 业务逻辑

#### 情况 A：首次存储（创建账户）

```rust
if **account_data.try_borrow_lamports().unwrap() == 0 {
    // 账户不存在，创建新账户
    solana_program::program::invoke_signed(
        &solana_program::system_instruction::create_account(...),
        accounts,
        &[&[&account_user.key.to_bytes(), &[bump_seed]]],  // PDA 签名
    )?;
    account_data.data.borrow_mut().copy_from_slice(data);
    return Ok(());
}
```

#### 情况 B：数据变大，补充租金

```rust
if rent_exemption > account_data.lamports() {
    solana_program::program::invoke(
        &solana_program::system_instruction::transfer(...),
        accounts,
    )?;
}
```

#### 情况 C：数据变小，退还费用

```rust
if rent_exemption < account_data.lamports() {
    **account_user.lamports.borrow_mut() = 
        account_user.lamports() + account_data.lamports() - rent_exemption;
    **account_data.lamports.borrow_mut() = rent_exemption;
}
```

注意：这里直接修改余额而不是调用系统指令，因为 PDA 归程序所有。

#### 更新数据

```rust
account_data.realloc(data.len(), false)?;  // 调整空间
account_data.data.borrow_mut().copy_from_slice(data);  // 写入数据
```

---

## 构建与部署

### 1. 构建程序

```bash
cargo build-sbf
```

这会在 `target/deploy/` 目录生成 `pxsol_ss.so` 文件。

### 2. 启动本地测试网络

```bash
# 在后台运行
solana-test-validator &

# 或在新终端窗口运行
solana-test-validator
```

### 3. 配置 Solana CLI（可选）

```bash
# 设置使用本地网络
solana config set --url localhost

# 查看配置
solana config get
```

### 4. 给测试钱包空投 SOL

```bash
solana airdrop 100 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt --url http://127.0.0.1:8899
```

### 5. 运行部署脚本

```bash
# 激活虚拟环境
source .venv/bin/activate

# 部署
python deploy.py
```

成功后会输出程序地址，例如：
```
"A5S8R7wkjhUoANf2AvNyYSMUxY5wse46VkYEo3Go4pE2"
```

### 部署脚本解析 (deploy.py)

```python
import pathlib
import pxsol

# 启用日志
pxsol.config.current.log = 1

# 创建钱包（使用测试私钥 0x01）
ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

# 读取编译后的程序二进制文件
program_data = pathlib.Path('target/deploy/pxsol_ss.so').read_bytes()

# 部署程序
program_pubkey = ada.program_deploy(bytearray(program_data))

# 输出程序地址
print(program_pubkey)
```

---

## 使用指南

### 前端调用示例 (JavaScript/TypeScript)

```typescript
import {
  Connection,
  PublicKey,
  Transaction,
  TransactionInstruction,
  SystemProgram,
  SYSVAR_RENT_PUBKEY,
} from '@solana/web3.js';

// 程序 ID（部署后获得）
const PROGRAM_ID = new PublicKey('A5S8R7wkjhUoANf2AvNyYSMUxY5wse46VkYEo3Go4pE2');

// 计算用户的数据账户地址（PDA）
function getDataAccountAddress(userPubkey: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [userPubkey.toBytes()],
    PROGRAM_ID
  );
}

// 存储数据
async function storeData(
  connection: Connection,
  userPubkey: PublicKey,
  data: Uint8Array
): Promise<Transaction> {
  const [dataAccount] = getDataAccountAddress(userPubkey);

  const instruction = new TransactionInstruction({
    keys: [
      { pubkey: userPubkey, isSigner: true, isWritable: true },
      { pubkey: dataAccount, isSigner: false, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: SYSVAR_RENT_PUBKEY, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data: Buffer.from(data),
  });

  const transaction = new Transaction().add(instruction);
  return transaction;
}

// 读取数据
async function readData(
  connection: Connection,
  userPubkey: PublicKey
): Promise<Uint8Array | null> {
  const [dataAccount] = getDataAccountAddress(userPubkey);
  
  const accountInfo = await connection.getAccountInfo(dataAccount);
  if (!accountInfo) {
    return null;
  }
  
  return accountInfo.data;
}
```

### Python 调用示例

```python
import pxsol

# 配置网络
pxsol.config.current = pxsol.config.Config.devnet()  # 或 mainnet()

# 创建钱包
wallet = pxsol.wallet.Wallet(pxsol.core.PriKey.generate())

# 程序地址
program_id = pxsol.core.PubKey.base58_decode("A5S8R7wkjhUoANf2AvNyYSMUxY5wse46VkYEo3Go4pE2")

# 计算 PDA
data_account, bump = pxsol.core.PubKey.find_program_address(
    [wallet.pubkey.p],
    program_id
)

# 调用程序存储数据
# ... (需要构建交易)
```

---

## Web2 vs Solana 概念对照

| Web2 概念 | Solana 概念 | 详细说明 |
|-----------|-------------|----------|
| 服务器 | 验证节点 (Validator) | 运行程序、处理交易的节点 |
| 数据库 | 账户 (Account) | 链上存储数据的单位 |
| API 接口 | 程序 (Program) | 部署在链上的代码 |
| HTTP 请求 | 交易 (Transaction) | 一次链上操作 |
| 请求参数 | 指令数据 (Instruction Data) | 传给程序的参数 |
| Session/Token | 签名 (Signature) | 证明身份和授权 |
| 用户 ID | 公钥 (Public Key) | 用户的唯一标识 |
| 密码 | 私钥 (Private Key) | 用于签名，证明身份 |
| 托管账户 | PDA | 由程序控制的账户 |
| 存储费 | 租金 (Rent) | 占用链上存储需要付费 |
| 美分 | Lamports | SOL 的最小单位 |

---

## 常见问题

### Q: 为什么需要 PDA？

A: PDA 解决了一个问题：程序需要拥有账户来存储数据，但普通账户需要私钥签名。PDA 没有私钥，只有生成它的程序可以代表它签名。

### Q: 租金会被扣光吗？

A: 不会。只要账户余额超过"租金豁免"金额，就永远不会被扣租金。这个程序会自动管理这个金额。

### Q: 如何部署到主网？

A: 
1. 修改 `deploy.py` 配置使用主网 RPC
2. 使用真实钱包（有真实 SOL）
3. 运行部署脚本

```python
pxsol.config.current = pxsol.config.Config.mainnet()
```

### Q: 程序部署后可以更新吗？

A: 可以，但需要使用"可升级程序"模式部署。默认部署是不可变的。

---

## 快速参考

### 完整部署命令

```bash
# 1. 构建程序
cargo build-sbf

# 2. 启动本地验证器（新终端）
solana-test-validator

# 3. 激活 Python 环境
source .venv/bin/activate

# 4. 空投测试资金
solana airdrop 100 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt --url http://127.0.0.1:8899

# 5. 部署
python deploy.py
```

### 环境要求

- Rust 1.70+
- Solana CLI 1.18+
- Python 3.10+ (推荐 3.11)
- pxsol 0.4.2

---

## 相关资源

- [Solana 官方文档](https://docs.solana.com/)
- [Solana Cookbook](https://solanacookbook.com/) - 实用代码示例
- [Anchor Framework](https://anchor-lang.com/) - Solana 开发框架
- [pxsol GitHub](https://github.com/mohanson/pxsol) - Python Solana SDK

---

*文档最后更新: 2026-01-08*
