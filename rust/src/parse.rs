use crate::constants;

use std::{collections::HashMap, fs::File, path::Path};

use anyhow::Result;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct Ability {}

#[derive(Serialize, Deserialize, Debug)]
struct AbilityDex {
    #[serde(flatten)]
    ability: HashMap<String, Ability>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct Data {}

#[derive(Serialize, Deserialize, Debug)]
struct DataDex {
    #[serde(flatten)]
    data: HashMap<String, Data>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct Item {}

#[derive(Serialize, Deserialize, Debug)]
struct ItemDex {
    #[serde(flatten)]
    item: HashMap<String, Item>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct Learnset {}

#[derive(Serialize, Deserialize, Debug)]
struct LearnsetDex {
    #[serde(flatten)]
    learnset: HashMap<String, Learnset>,
}

#[derive(Serialize, Deserialize, Debug)]
enum Category {
    Physical,
    Special,
    Status,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct Move {
    exists: bool,
    num: u16,
    accuracy: Value,
    base_power: u16,
    category: Category,
    name: String,
    pp: u8,
    priority: i16,
}

#[derive(Serialize, Deserialize, Debug)]
struct MoveDex {
    #[serde(flatten)]
    moves: HashMap<String, Move>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct Species {}

#[derive(Serialize, Deserialize, Debug)]
struct SpeciesDex {
    #[serde(flatten)]
    species: HashMap<String, Species>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
struct Typechart {}

#[derive(Serialize, Deserialize, Debug)]
struct TypechartDex {
    #[serde(flatten)]
    typechart: HashMap<String, Typechart>,
}

#[derive(Debug)]
#[allow(dead_code)]
pub struct Dexes {
    ability: AbilityDex,
    data: DataDex,
    item: ItemDex,
    learnset: LearnsetDex,
    moves: MoveDex,
    species: SpeciesDex,
    typechart: TypechartDex,
}

#[allow(dead_code)]
pub fn dex_data() -> Result<Dexes> {
    let data_path = Path::new(constants::DATA_DIR);

    let ability_dex_path = data_path.join("ability_dex.json");
    let ability_dex_file = File::open(ability_dex_path)?;
    let ability: AbilityDex = serde_json::from_reader(ability_dex_file)?;

    let data_dex_path = data_path.join("data_dex.json");
    let data_dex_file = File::open(data_dex_path)?;
    let data: DataDex = serde_json::from_reader(data_dex_file)?;

    let item_dex_path = data_path.join("items_dex.json");
    let item_dex_file = File::open(item_dex_path)?;
    let item: ItemDex = serde_json::from_reader(item_dex_file)?;

    let learnset_dex_path = data_path.join("learnsets_dex.json");
    let learnset_dex_file = File::open(learnset_dex_path)?;
    let learnset: LearnsetDex = serde_json::from_reader(learnset_dex_file)?;

    let move_dex_path = data_path.join("moves_dex.json");
    let move_dex_file = File::open(move_dex_path)?;
    let moves: MoveDex = serde_json::from_reader(move_dex_file)?;

    let species_dex_path = data_path.join("species_dex.json");
    let species_dex_file = File::open(species_dex_path)?;
    let species: SpeciesDex = serde_json::from_reader(species_dex_file)?;

    let typechart_dex_path = data_path.join("typechart_dex.json");
    let typechart_dex_file = File::open(typechart_dex_path)?;
    let typechart: TypechartDex = serde_json::from_reader(typechart_dex_file)?;

    Ok(Dexes {
        ability,
        data,
        item,
        learnset,
        moves,
        species,
        typechart,
    })
}
