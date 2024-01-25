use pest::{iterators::Pairs, Parser};
use pest_derive::Parser;

#[derive(Parser)]
#[grammar = "battle/battle.pest"]
struct BattleParser;

pub fn parse<S: AsRef<str>>(input: &S) -> Result<Pairs<'_, Rule>, Box<pest::error::Error<Rule>>> {
    match BattleParser::parse(Rule::battle, input.as_ref()) {
        Ok(pairs) => Ok(pairs),
        Err(e) => Err(Box::new(e)),
    }
}
