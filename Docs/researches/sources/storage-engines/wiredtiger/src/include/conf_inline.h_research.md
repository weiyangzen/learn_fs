# sources/storage-engines/wiredtiger/src/include/conf_inline.h

## Purpose
`conf_inline.h` provides small, hot inline helpers for compiled configuration detection, validation, default lookup, and hex decoding. It keeps common config operations close to call sites without forcing full parser logic into every user.

## Important APIs, Types, and Functions
`__wt_conf_is_compiled` checks whether a config pointer lies inside `conn->conf_dummy`; `__wt_conf_get_compiled` converts that dummy pointer offset into `conn->conf_array[]`. `__wt_conf_check_choice` validates string choices and canonicalizes successful matches to generated `__WT_CONFIG_CHOICE_*` string addresses, enabling `WT_CONF_STRING_MATCH` pointer comparisons.

`__wt_conf_check_one` runs any custom check function, choice checks, and numeric min/max validation from `WT_CONFIG_CHECK`. `__wt_conf_gets_def_func` implements the fast default path for callers supplying an override default. `__wt_conf_parse_hex` parses up to 64 bits of hexadecimal text with explicit invalid-character and length errors.

## Control Flow
Compiled config callers pass a dummy string. The inline detection path treats it as an index into the connection's compiled config array. Validation of each value is layered: custom callback first, then generic choice/min/max checks only when a check string exists. Default lookup short-circuits through the compiled config bitmap before falling back to the full lookup function.

## State and Persistence Behavior
The helpers mutate only returned `WT_CONFIG_ITEM` values and choice string pointers. Canonicalizing choices changes `value->str` from the original input span to a generated static choice string, which is intentionally stable for pointer comparisons. No durable state is written.

## Dependencies and Integration Points
The file depends on `WT_CONNECTION_IMPL` compiled config arrays, `WT_CONFIG_CHECK`, `WT_CONFIG_ITEM`, generated choice symbols from `config.h`, and WiredTiger error macros. It is used by compiled config accessors and by compilation/checking code that wants fast validation in headers.

## Risks and Edge Cases
Pointer-range compiled detection assumes dummy config pointers are never forged and that `conf_dummy`/`conf_size` accurately cover the dummy string table. Blank strings are legal choices only through `__WT_CONFIG_CHOICE_NULL`, which can surprise callers expecting ordinary choice text. Hex parsing uses character values as table indexes and rejects strings longer than 16 hex digits to avoid overflow.

## Test Signals
Tests should compare compiled and uncompiled config lookup results, verify choice canonicalization including blank choices, assert min/max failure messages, and exercise invalid/too-long hex strings. Fuzzing config input should reach `__wt_conf_parse_hex` and choice validation.
