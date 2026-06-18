# sources/test-tools/ior/src/option.h

Purpose: defines the option table schema and parser API.

Important APIs and types: `option_value_type` distinguishes flags, optional arguments, and required arguments. `option_help` describes one option: short name, long name, help text, argument kind, data type code, and destination variable/function pointer. `option_module` groups options under an optional prefix and backend defaults. `options_all_t` stores all modules. `LAST_OPTION` terminates option arrays.

Control flow and integration: applications build arrays of `option_help`, combine them into `options_all_t` via AIORI helpers or local code, and call `option_parse()`, `option_parse_str()`, or `option_parse_key_value()`. `option_merge()` supports combining static option arrays.

State and persistence: no own state. The schema points directly to mutable caller variables, so option table lifetime and destination object lifetime must outlive parsing.

Risks: type codes are untyped characters (`d`, `l`, `u`, `s`, `H`, `f`, `F`, `c`, `p`), so mismatches between `type` and `variable` are compile-time invisible. `LAST_OPTION` depends on a zeroed sentinel. The name `OPTION_OPTIONAL_ARGUMENT` is misleading because the parser still fails if the option is present without an argument.

Test signals: compile checks for sentinel usage, parser tests for each type code, and C/C++ compatibility when included from test programs.
