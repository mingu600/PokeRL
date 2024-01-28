#![feature(once_cell_try)]

use anyhow::Result;
use log::trace;
use std::{
    fs::{self, File},
    io::{BufReader, Read},
};

mod battle;
mod constants;
mod dex;

fn main() -> Result<()> {
    env_logger::init();

    let battle_logs = fs::read_dir(constants::RANDOM_BATTLE_LOG_DIR)?;
    for log_file in battle_logs {
        let log_file_path = log_file?.path();
        trace!("Loading battle log: {:?}", &log_file_path);
        let game_file = File::open(&log_file_path)?;

        let mut game_string = String::new();
        BufReader::new(game_file).read_to_string(&mut game_string)?;

        trace!("Parsing battle log: {:?}", &log_file_path);
        let _random_battle = battle::Battle::new(&game_string)?;
        // println!("{:?}", random_battle);
    }

    // println!("{:?}", dex_data);
    // constants::MAX_MOVE_COUNT;

    Ok(())
}
