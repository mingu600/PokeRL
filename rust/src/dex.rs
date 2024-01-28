#![allow(dead_code)] // TODO: remove

use crate::constants;

use std::{
    collections::{BTreeMap, HashMap},
    fs::File,
    io::BufReader,
    path::Path,
    sync::OnceLock,
};

use anyhow::Result;
use log::info;
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
            macro_rules! load_dex {
                ($t:ty, $s:literal, $f:ident) => {{
                    let data_path = Path::new(constants::DATA_DIR);
                    let dex_path = data_path.join($s);
                    let dex_file = File::open(dex_path)?;
                    let dex_reader = BufReader::new(dex_file);
                    let dex: $t = serde_json::from_reader(dex_reader)?;
                    dex.$f
                }};
            }
            info!("Loading dexes");

            Ok(Self {
                ability: load_dex!(AbilityDex, "ability_dex.json", abilities),
                data: load_dex!(DataDex, "data_dex.json", data),
                item: load_dex!(ItemDex, "items_dex.json", items),
                learnset: load_dex!(LearnsetDex, "learnsets_dex.json", learnsets),
                moves: load_dex!(MoveDex, "moves_dex.json", moves),
                species: load_dex!(SpeciesDex, "species_dex.json", species),
                typechart: load_dex!(TypechartDex, "typechart_dex.json", typecharts),
            })
        })
    }
}
