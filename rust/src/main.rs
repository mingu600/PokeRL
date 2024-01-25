use std::{
    error::Error,
    fs::File,
    io::{BufReader, Read},
    path::Path,
};

mod battle;
mod constants;
mod parse;

fn main() -> Result<(), Box<dyn Error>> {
    let game_file = File::open(Path::new(constants::DATA_DIR).join("random_battle.txt"))?;
    let mut game_string = String::new();
    BufReader::new(game_file).read_to_string(&mut game_string)?;
    let random_battle = battle::parse(&game_string)?;
    for pair in random_battle {
        println!("{pair:#?}");
    }

    // let dex_data = parse::dex_data()?;

    // println!("{:?}", dex_data);
    // constants::MAX_MOVE_COUNT;

    Ok(())
}
