use const_format::formatcp;

pub const DATA_DIR: &str = "../data";
pub const BATTLE_LOGS_DIR: &str = "/battle_logs";
pub const RANDOM_BATTLE_LOG_DIR: &str =
    formatcp!("{DATA_DIR}{BATTLE_LOGS_DIR}{}", "/random_battle");

#[allow(dead_code)]
pub static MAX_MOVE_COUNT: u8 = 4;
