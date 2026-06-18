# sources/storage-engines/wiredtiger/test/cppsuite/src/util/options_parser.cpp

## Purpose
Implements two minimal command-line helpers for detecting an option and reading the following argument as its value.

## Important APIs, Types, And Functions
`option_exists(const std::string &opt, int argc, char *argv[])` and `value_for_opt(const std::string &opt, int argc, char *argv[])`.

## Control Flow
Both functions loop over `argv`, convert each argument to `std::string`, and use substring `find(opt)`. `option_exists` returns true on first match. `value_for_opt` returns the next argv element for the first match, or empty string if the match is last or absent.

## State And Persistence Behavior
No state is stored and no persistence occurs.

## Dependencies And Integration Points
Depends only on `options_parser.h`. Intended for cppsuite test runners or utilities that parse simple flags.

## Risks And Test Signals
Substring matching can produce false positives, for example `--home` matching `--homepage`. Values are positional and cannot distinguish `--opt=value` formats. Empty string can mean absent option or present-without-value.
