# sources/storage-engines/rocksdb/tools/advisor/advisor/ini_parser.py

## Purpose

`ini_parser.py` provides lightweight parsing helpers for the Advisor rules/spec syntax and is reused by the OPTIONS parser for simple key/value handling.

## Important APIs, Types, and Functions

`IniParser.Element` classifies `rule`, `cond`, `sugg`, `key_val`, and `comment`. Static helpers are `remove_trailing_comment`, `is_section_header`, `get_section_name`, `get_element`, `get_key_value_pair`, and `get_list_from_value`.

## Control Flow

Each line has trailing comments stripped, then is classified as empty/comment, section header, or key/value. Section headers are identified by square brackets and by a section type prefix. Key/value parsing splits at the first `=`, preserves embedded `=`, returns `None` for empty values, and converts colon-separated values to lists only when more than one token is present.

## State and Persistence Behavior

The parser is stateless and performs no I/O itself.

## Dependencies and Integration Points

It depends only on `Enum`. `RulesSpec` uses it for rule sections; `OptionsSpecParser` inherits its comment and key/value utilities.

## Risks and Test Signals

Risks include treating `#` inside values as a comment, no escaping/quoting semantics for lists, strict section-name quoting, and no duplicate detection. Tests cover missing section names, missing values, list parsing indirectly through rules/options, and parse errors for unrecognized lines.
