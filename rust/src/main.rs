use anyhow::Result;
use std::{
    fs::{self, File},
    io::{BufReader, Read},
};

mod battle;
mod constants;
mod parse;

fn main() -> Result<()> {
    let battle_logs = fs::read_dir(constants::RANDOM_BATTLE_LOG_DIR)?;
    for log_file in battle_logs {
        let game_file = File::open(log_file?.path())?;

        let mut game_string = String::new();

        BufReader::new(game_file).read_to_string(&mut game_string)?;
        let random_battle = battle::parse(&game_string)?;

        // for pair in random_battle {
        //     println!("{pair:#?}");
        // }
    }

    // let dex_data = parse::dex_data()?;

    // println!("{:?}", dex_data);
    // constants::MAX_MOVE_COUNT;

    Ok(())
}
