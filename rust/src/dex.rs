use crate::constants;

use std::{
    collections::{BTreeMap, HashMap},
    fs::File,
    io::BufReader,
    path::Path,
    sync::OnceLock,
};

use anyhow::Result;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Ability {
    pub name: String,
    pub num: i16,
    pub gen: u8,
}

#[derive(Serialize, Deserialize, Debug)]
struct AbilityDex {
    #[serde(flatten)]
    abilities: HashMap<String, Ability>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Data {}

#[derive(Serialize, Deserialize, Debug)]
struct DataDex {
    #[serde(flatten)]
    data: HashMap<String, Data>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Item {}

#[derive(Serialize, Deserialize, Debug)]
struct ItemDex {
    #[serde(flatten)]
    items: HashMap<String, Item>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Learnset {}

#[derive(Serialize, Deserialize, Debug)]
struct LearnsetDex {
    #[serde(flatten)]
    learnsets: HashMap<String, Learnset>,
}

#[derive(Serialize, Deserialize, Debug)]
pub enum Category {
    Physical,
    Special,
    Status,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Move {
    pub exists: bool,
    pub num: u16,
    pub accuracy: Value,
    pub base_power: u16,
    pub category: Category,
    pub name: String,
    pub pp: u8,
    pub priority: i16,
}

#[derive(Serialize, Deserialize, Debug)]
struct MoveDex {
    #[serde(flatten)]
    moves: HashMap<String, Move>,
}

#[allow(clippy::upper_case_acronyms, non_camel_case_types)]
#[derive(Serialize, Deserialize, Debug)]
pub enum SmogonTier {
    #[serde(rename = "CAP LC")]
    CAP_LC,

    #[serde(rename = "CAP NFE")]
    CAP_NFE,

    CAP,
    NFE,
    AG,
    Illegal,
    LC,
    NU,
    NUBL,
    OU,
    PU,
    PUBL,
    RU,
    RUBL,
    UU,
    UUBL,
    Uber,
    Unreleased,
    ZU,
    ZUBL,
}

#[derive(Serialize, Deserialize, Debug)]
pub enum PokemonType {
    Normal,
    Fire,
    Fighting,
    Water,
    Bird,
    Flying,
    Grass,
    Poison,
    Electric,
    Ground,
    Psychic,
    Rock,
    Ice,
    Bug,
    Dragon,
    Ghost,
    Dark,
    Steel,
    Fairy,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Species {
    pub name: String,
    pub num: i16,
    pub tier: SmogonTier,
    pub gen: u8,
    pub abilities: BTreeMap<String, String>,
    pub types: Vec<PokemonType>,
    pub base_species: String,
    pub forme: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct SpeciesDex {
    #[serde(flatten)]
    species: HashMap<String, Species>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Typechart {}

#[derive(Serialize, Deserialize, Debug)]
struct TypechartDex {
    #[serde(flatten)]
    typecharts: HashMap<String, Typechart>,
}

#[derive(Debug)]
#[allow(dead_code)]
pub struct Dexes {
    // #[serde(flatten)]
    pub ability: HashMap<String, Ability>,
    pub data: HashMap<String, Data>,
    pub item: HashMap<String, Item>,
    pub learnset: HashMap<String, Learnset>,
    pub moves: HashMap<String, Move>,
    pub species: HashMap<String, Species>,
    pub typechart: HashMap<String, Typechart>,
}

static DEXES: OnceLock<Dexes> = OnceLock::new();

impl Dexes {
    /// This serde parses the dex JSONs the first time this is called.
    /// Subsequent calls refer to the initialzed static.
    pub fn new() -> Result<&'static Self> {
        DEXES.get_or_try_init(|| -> Result<Self> {
            let data_path = Path::new(constants::DATA_DIR);

            let ability_dex_path = data_path.join("ability_dex.json");
            let ability_dex_file = File::open(ability_dex_path)?;
            let ability_dex_reader = BufReader::new(ability_dex_file);
            let ability_dex: AbilityDex = serde_json::from_reader(ability_dex_reader)?;

            let data_dex_path = data_path.join("data_dex.json");
            let data_dex_file = File::open(data_dex_path)?;
            let data_dex_reader = BufReader::new(data_dex_file);
            let data_dex: DataDex = serde_json::from_reader(data_dex_reader)?;

            let item_dex_path = data_path.join("items_dex.json");
            let item_dex_file = File::open(item_dex_path)?;
            let item_dex_reader = BufReader::new(item_dex_file);
            let item_dex: ItemDex = serde_json::from_reader(item_dex_reader)?;

            let learnset_dex_path = data_path.join("learnsets_dex.json");
            let learnset_dex_file = File::open(learnset_dex_path)?;
            let learnset_dex_reader = BufReader::new(learnset_dex_file);
            let learnset_dex: LearnsetDex = serde_json::from_reader(learnset_dex_reader)?;

            let move_dex_path = data_path.join("moves_dex.json");
            let move_dex_file = File::open(move_dex_path)?;
            let move_dex_reader = BufReader::new(move_dex_file);
            let move_dex: MoveDex = serde_json::from_reader(move_dex_reader)?;

            let species_dex_path = data_path.join("species_dex.json");
            let species_dex_file = File::open(species_dex_path)?;
            let species_dex_reader = BufReader::new(species_dex_file);
            let species_dex: SpeciesDex = serde_json::from_reader(species_dex_reader)?;

            let typechart_dex_path = data_path.join("typechart_dex.json");
            let typechart_dex_file = File::open(typechart_dex_path)?;
            let typechart_dex_reader = BufReader::new(typechart_dex_file);
            let typechart_dex: TypechartDex = serde_json::from_reader(typechart_dex_reader)?;

            Ok(Dexes {
                ability: ability_dex.abilities,
                data: data_dex.data,
                item: item_dex.items,
                learnset: learnset_dex.learnsets,
                moves: move_dex.moves,
                species: species_dex.species,
                typechart: typechart_dex.typecharts,
            })
        })
    }
}
