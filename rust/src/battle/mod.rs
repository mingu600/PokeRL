use anyhow::{anyhow, Result};
use pest::{iterators::Pairs, Parser};
use pest_derive::Parser;
use std::str::FromStr;
use strum_macros::EnumString;

#[derive(Parser)]
#[grammar = "battle/battle.pest"]
struct BattleParser;

#[derive(Debug)]
pub enum Gender {
    None,
    Male,
    Female,
}

#[derive(Debug)]
pub struct Move {}

#[derive(Debug)]
pub struct Pokemon {
    nickname: String,
    species: String,
    moves: Vec<Move>,
    level: u8,
    gender: Gender,
    ability: String,
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
                        index: player_index
                            .chars()
                            .nth(1)
                            .ok_or_else(|| anyhow!("Player index invalid: {player_index}"))?
                            .to_digit(10)
                            .ok_or_else(|| anyhow!("Player index invalid: {player_index}"))?,
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

    pub fn new<S: AsRef<str>>(input: &S) -> Result<Battle> {
        let battle_parser = Self::parse(input)?;
        let mut prelude: Result<Prelude> = Err(anyhow!("Prelude not in battle"));

        for pair in battle_parser {
            match pair.as_rule() {
                Rule::prelude => prelude = Self::parse_prelude(pair.into_inner()),
                Rule::turns => {
                    for turn in pair.into_inner() {
                        match turn.as_rule() {
                            // Rule::turn_section => println!("Turn section: {:?}", turn.as_str()),
                            _ => (),
                        }
                    }
                }
                _ => (),
            }
        }

        println!("{:#?}", prelude?);

        Ok(Self { teams: vec![] })
    }
}
