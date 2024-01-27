use anyhow::{anyhow, Result};
use pest::{iterators::Pairs, Parser};
use pest_derive::Parser;
use std::{fmt::Display, ops::Not, str::FromStr};
use strum_macros::EnumString;

use crate::dex;

#[derive(Parser)]
#[grammar = "battle/battle.pest"]
struct BattleParser;

#[derive(Debug, EnumString)]
pub enum Gender {
    None,
    #[strum(serialize = "M")]
    Male,
    #[strum(serialize = "F")]
    Female,
}

#[derive(Debug)]
pub struct Move {}

#[derive(Debug)]
pub struct HP {
    current: u16,
    max: u16,
}

#[derive(Debug)]
pub struct Pokemon {
    nickname: String,
    species: String,
    forme: Option<String>,
    moves: Vec<Move>,
    level: u8,
    gender: Gender,
    ability: Option<String>,
    hp: HP,
}

#[derive(Debug)]
pub struct Team {
    player: String,
    index: u32,
    pokemon: Vec<Pokemon>,
}

#[derive(Debug, EnumString)]
#[strum(serialize_all = "snake_case")]
pub enum Gametype {
    Singles,
    Doubles,
    Triples,
    Multi,
    FreeForAll,
}

#[derive(Debug)]
pub struct ShowdownRule {
    name: String,
    message: String,
}

#[derive(Debug)]
struct Prelude {
    teams: Vec<Team>,
    gen: u8,
    tier: String,
    gametype: Gametype,
    teamsize: u8,
    rated: bool,
    rules: Vec<ShowdownRule>,
}

#[derive(Debug)]
struct Switch {
    field_position: String,
    pokemon: Pokemon,
}

#[derive(Debug)]
enum TurnEvent {
    Switch(Switch),
}

#[derive(Debug)]
pub struct Battle {
    teams: Vec<Team>,
}

impl Battle {
    fn parse<S: AsRef<str>>(input: &S) -> Result<Pairs<'_, Rule>> {
        match BattleParser::parse(Rule::battle, input.as_ref()) {
            Ok(pairs) => Ok(pairs),
            Err(e) => Err(anyhow!(e)),
        }
    }

    fn parse_player_index<S>(player_index: &S) -> Result<u32>
    where
        S: AsRef<str> + Display,
    {
        player_index
            .as_ref()
            .chars()
            .nth(1)
            .ok_or_else(|| anyhow!("Player index invalid: {player_index}"))?
            .to_digit(10)
            .ok_or_else(|| anyhow!("Player index invalid: {player_index}"))
    }

    fn parse_prelude(prelude: Pairs<'_, Rule>) -> Result<Prelude> {
        let mut teams = vec![];
        let mut gen: Result<u8> = Err(anyhow!("Gen not found in battle"));
        let mut tier: Result<String> = Err(anyhow!("Tier not found in battle"));
        let mut gametype: Result<Gametype> = Err(anyhow!("Gametype not found in battle"));
        let mut teamsize: Result<u8> = Err(anyhow!("Teamsize not found in battle"));
        let mut rated = false;
        let mut rules = vec![];

        for prelude_line in prelude {
            match prelude_line.as_rule() {
                Rule::player => {
                    let mut username: &str = "";
                    let mut player_index: &str = "";
                    for player_section in prelude_line.into_inner() {
                        match player_section.as_rule() {
                            Rule::username => username = player_section.as_str(),
                            Rule::player_index => player_index = player_section.as_str(),
                            _ => (),
                        }
                    }

                    teams.push(Team {
                        player: username.to_string(),
                        index: Self::parse_player_index(&player_index)?,
                        pokemon: vec![],
                    });
                }

                Rule::gen => gen = Ok(prelude_line.as_str().parse::<u8>()?),
                Rule::tier => tier = Ok(prelude_line.as_str().to_string()),
                Rule::gametype => gametype = Ok(Gametype::from_str(prelude_line.as_str())?),
                Rule::teamsize => {
                    for inner in prelude_line.into_inner() {
                        if inner.as_rule() == Rule::teamsize_number {
                            teamsize = Ok(inner.as_str().parse::<u8>()?);
                        }
                    }
                }
                Rule::rated => rated = true,
                Rule::showdown_rule => {
                    let mut rule_name: &str = "";
                    let mut rule_message: &str = "";
                    for inner in prelude_line.into_inner() {
                        match inner.as_rule() {
                            Rule::rule_name => rule_name = inner.as_str(),
                            Rule::rule_description => rule_message = inner.as_str(),
                            _ => (),
                        }
                    }
                    rules.push(ShowdownRule {
                        name: rule_name.to_string(),
                        message: rule_message.to_string(),
                    });
                }
                _ => (),
            }
        }

        Ok(Prelude {
            teams,
            gen: gen?,
            tier: tier?,
            gametype: gametype?,
            teamsize: teamsize?,
            rated,
            rules,
        })
    }

    fn parse_species<S: AsRef<str>>(name: &S) -> Result<(String, Option<String>)> {
        let dexes = dex::Dexes::new()?;
        let dex_entry = {
            dexes
                .species
                .get(&name.as_ref().to_lowercase().replace(['-', ' '], ""))
                .or_else(|| {
                    dexes
                        .species
                        .get(name.as_ref().to_lowercase().split('-').next()?)
                })
        }
        .ok_or_else(|| anyhow!("Pokemon not found in species dex: {}", name.as_ref()))?;

        Ok((
            dex_entry.base_species.clone(),
            dex_entry
                .forme
                .is_empty()
                .not()
                .then(|| dex_entry.forme.clone()),
        ))
    }

    fn parse_switch(switch_line: Pairs<'_, Rule>) -> Result<Switch> {
        let base_not_found = format!("not found in switch line: `{}`", switch_line.as_str());

        let mut field_position: Result<String> = Err(anyhow!("Field position {base_not_found}"));
        let mut nickname: Result<String> = Err(anyhow!("Pokemon nickname {base_not_found}"));
        let mut level = 100;
        let mut gender = Gender::None;
        let mut hp = HP { current: 0, max: 0 };
        let mut species: Result<String> = Err(anyhow!("Species {base_not_found}"));
        let mut forme: Option<String> = None;

        for switch in switch_line {
            match switch.as_rule() {
                Rule::switch_name => {
                    for part in switch.into_inner() {
                        match part.as_rule() {
                            Rule::field_position => field_position = Ok(part.as_str().to_string()),
                            Rule::poke_nickname => nickname = Ok(part.as_str().to_string()),
                            _ => (),
                        }
                    }
                }
                Rule::poke_details => {
                    for detail in switch.into_inner() {
                        match detail.as_rule() {
                            Rule::poke_name => {
                                let (parsed_species, parsed_forme) =
                                    Self::parse_species(&detail.as_str())?;

                                species = Ok(parsed_species);
                                forme = parsed_forme;
                            }
                            Rule::poke_level => level = detail.as_str().parse()?,
                            Rule::poke_gender => gender = Gender::from_str(detail.as_str())?,
                            _ => (),
                        }
                    }
                }
                Rule::poke_hp_status => {
                    let mut cur_hp: Result<u16> =
                        Err(anyhow!("Current HP not found in switch line"));
                    let mut max_hp: Result<u16> = Err(anyhow!("Max HP not found in switch line"));

                    for hp_part in switch.into_inner() {
                        match hp_part.as_rule() {
                            Rule::poke_cur_hp => cur_hp = Ok(hp_part.as_str().parse()?),
                            Rule::poke_max_hp => max_hp = Ok(hp_part.as_str().parse()?),
                            _ => (),
                        }
                    }

                    hp = HP {
                        current: cur_hp?,
                        max: max_hp?,
                    };
                }

                _ => (),
            }
        }

        Ok(Switch {
            field_position: field_position?,
            pokemon: Pokemon {
                nickname: nickname?,
                species: species?,
                forme,
                moves: vec![],
                level,
                gender,
                ability: None,
                hp,
            },
        })
    }

    fn parse_turns(turns: Pairs<'_, Rule>) -> Result<Vec<TurnEvent>> {
        let mut turn_list = vec![];

        for turn in turns {
            if turn.as_rule() == Rule::turn_section {
                for turn_line in turn.into_inner() {
                    match turn_line.as_rule() {
                        Rule::switch => {
                            let switched_mon = Self::parse_switch(turn_line.into_inner())?;
                            turn_list.push(TurnEvent::Switch(switched_mon));
                        }
                        _ => (),
                    }
                }
            }
        }

        Ok(turn_list)
    }

    pub fn new<S: AsRef<str>>(input: &S) -> Result<Self> {
        let battle_parser = Self::parse(input)?;
        let mut prelude: Result<Prelude> = Err(anyhow!("Prelude not in battle"));
        let mut turns: Vec<_> = vec![];

        for pair in battle_parser {
            match pair.as_rule() {
                Rule::prelude => prelude = Self::parse_prelude(pair.into_inner()),
                Rule::turns => turns = Self::parse_turns(pair.into_inner())?,
                _ => (),
            }
        }

        let mut teams = prelude?.teams;

        for turn in turns {
            match turn {
                TurnEvent::Switch(switch) => {
                    let team_index = Self::parse_player_index(&switch.field_position)?;
                    let team_pokemon: &mut Team =
                        teams.get_mut((team_index - 1) as usize).ok_or_else(|| {
                            anyhow!("Tried to index into team that wasn't found in prelude")
                        })?;

                    if !team_pokemon
                        .pokemon
                        .iter()
                        .any(|p| p.nickname == switch.pokemon.nickname)
                    {
                        team_pokemon.pokemon.push(switch.pokemon)
                    }
                }
            }
        }

        Ok(Self { teams })
    }
}
