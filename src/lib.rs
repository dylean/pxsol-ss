//! # pxsol-ss: Solana 链上数据存储程序
//!
//! ## 功能特点
//! - 每个用户拥有一个专属的 PDA (Program Derived Address) 数据账户
//! - 自动管理存储费用（租金豁免）
//! - 支持数据的创建、更新和空间调整
//! - 数据变小时自动退还多余的 SOL
//!
//! ## 账户结构
//! 调用本程序需要传入以下账户（按顺序）：
//! 1. `account_user` - 用户账户（签名者，付款方）
//! 2. `account_data` - PDA 数据账户（存储用户数据）
//! 3. `system_program` - 系统程序
//! 4. `sysvar_rent` - 租金系统变量

#![allow(unexpected_cfgs)]

use solana_program::sysvar::Sysvar;

// 声明程序入口点，所有交易都会调用 process_instruction 函数
solana_program::entrypoint!(process_instruction);

/// 程序主入口函数
///
/// # 参数
/// - `program_id`: 本程序的公钥地址
/// - `accounts`: 参与本次交易的账户列表
/// - `data`: 用户要存储的数据（字节数组）
///
/// # 返回值
/// - `Ok(())`: 操作成功
/// - `Err(ProgramError)`: 操作失败，返回具体错误
///
/// # 业务逻辑
/// 1. 如果数据账户不存在 → 创建账户并写入数据
/// 2. 如果数据变大 → 补充租金费用
/// 3. 如果数据变小 → 退还多余费用
/// 4. 更新存储空间并写入新数据
pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    // =========================================================================
    // 第一步：解析账户列表
    // =========================================================================
    let accounts_iter = &mut accounts.iter();

    // 用户账户：交易的发起者，负责支付费用
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;

    // 数据账户：PDA 账户，用于存储用户数据
    let account_data = solana_program::account_info::next_account_info(accounts_iter)?;

    // 系统程序：用于创建账户和转账
    let _ = solana_program::account_info::next_account_info(accounts_iter)?;

    // 租金系统变量：用于计算租金豁免金额
    let _ = solana_program::account_info::next_account_info(accounts_iter)?;

    // =========================================================================
    // 第二步：计算租金豁免金额和 PDA bump seed
    // =========================================================================

    // 计算存储 data.len() 字节数据所需的最小 SOL 余额（租金豁免）
    // Solana 要求账户持有足够的 SOL 以避免被系统回收
    let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());

    // 计算 PDA 的 bump seed
    // PDA 地址 = hash(用户公钥 + bump_seed + program_id)
    // bump_seed 确保生成的地址不在 ed25519 曲线上（即没有对应的私钥）
    let bump_seed = solana_program::pubkey::Pubkey::find_program_address(
        &[&account_user.key.to_bytes()],
        program_id,
    )
    .1;

    // =========================================================================
    // 第三步：处理业务逻辑
    // =========================================================================

    // 情况 A：数据账户尚未初始化（余额为 0 表示账户不存在）
    // 需要创建新账户并写入数据
    if **account_data.try_borrow_lamports().unwrap() == 0 {
        // 使用 invoke_signed 调用系统程序创建账户
        // invoke_signed 允许程序代表 PDA 签名（因为 PDA 没有私钥）
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                account_user.key,  // 付款方
                account_data.key,  // 新账户地址
                rent_exemption,    // 初始余额（租金豁免金额）
                data.len() as u64, // 账户数据空间大小
                program_id,        // 账户所有者（本程序）
            ),
            accounts,
            // PDA 签名种子：[用户公钥, bump_seed]
            &[&[&account_user.key.to_bytes(), &[bump_seed]]],
        )?;

        // 将用户数据写入账户
        account_data.data.borrow_mut().copy_from_slice(data);
        return Ok(());
    }

    // 情况 B：数据变大，需要补充租金
    // 如果新数据需要的租金 > 当前账户余额，则需要用户补款
    if rent_exemption > account_data.lamports() {
        solana_program::program::invoke(
            &solana_program::system_instruction::transfer(
                account_user.key,                           // 付款方
                account_data.key,                           // 收款方
                rent_exemption - account_data.lamports(),   // 差额
            ),
            accounts,
        )?;
    }

    // 情况 C：数据变小，退还多余费用
    // 由于 PDA 账户归程序所有，可以直接修改余额而无需调用系统指令
    if rent_exemption < account_data.lamports() {
        // 将多余的 lamports 转给用户
        **account_user.lamports.borrow_mut() =
            account_user.lamports() + account_data.lamports() - rent_exemption;
        // 数据账户只保留必要的租金豁免金额
        **account_data.lamports.borrow_mut() = rent_exemption;
    }

    // =========================================================================
    // 第四步：更新数据
    // =========================================================================

    // 重新分配账户空间以匹配新数据大小
    // 参数 false 表示不用零填充新增的空间
    account_data.realloc(data.len(), false)?;

    // 将新数据写入账户
    account_data.data.borrow_mut().copy_from_slice(data);

    Ok(())
}
