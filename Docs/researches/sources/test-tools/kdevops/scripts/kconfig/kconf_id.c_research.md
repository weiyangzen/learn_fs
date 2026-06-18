# sources/test-tools/kdevops/scripts/kconfig/kconf_id.c

## Purpose
This file maps Kconfig language keywords to lexer/parser token metadata. It is a compact replacement for generated perfect-hash keyword lookup.

## Important APIs, Types, And Functions
`kconf_id_array[]` contains entries for commands and options such as `mainmenu`, `menu`, `choice`, `config`, `default`, `bool`, `tristate`, `select`, `imply`, `range`, `modules`, `defconfig_list`, and `allnoconfig_y`. Each entry carries a token, flags like `TF_COMMAND`, `TF_PARAM`, `TF_OPTION`, and for type/default tokens a symbol type. `kconf_id_lookup(str, len)` linearly searches the array.

## Control Flow
Lookup iterates the array, compares requested length with `strlen(id->name)`, and then `memcmp()`s the bytes. It returns the matching descriptor or `NULL`.

## State And Persistence
The keyword array is static read-only data at runtime. It has no persistent side effects.

## Dependencies And Integration Points
It requires the `struct kconf_id`, token constants, and flags from parser/lexer headers. The lexer/parser uses it to classify words when parsing Kconfig syntax.

## Risks And Test Signals
Linear lookup is fine for this small table but depends on all keywords being kept in sync with grammar tokens. Missing newer tokens will parse as ordinary words. Tests should parse Kconfig snippets for every listed keyword and reject/handle unknown keywords as expected.
