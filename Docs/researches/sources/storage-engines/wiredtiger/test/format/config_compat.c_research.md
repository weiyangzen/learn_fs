# sources/storage-engines/wiredtiger/test/format/config_compat.c

## Purpose
`config_compat.c` maps legacy format configuration names to the current dotted schema so old `CONFIG` files remain runnable.

## Important APIs, Types, And Functions
It defines `struct compat_list`, a static mapping array, and exports `void config_compat(const char **namep)`. The function receives a pointer to a config string and may redirect it to a static conversion buffer.

## Control Flow
`config_compat` ignores strings without `=`. For assignment strings, it compares the left-hand side including the equals sign against each legacy `orig` pattern. On match, it builds `current + original_value_suffix` in a static buffer and updates the caller's pointer.

## State And Persistence Behavior
The function has no durable state. It uses a single static `conv[100]`, so callers must consume the converted string before another conversion. The converted name then flows into normal config parsing and persistence through `config_single` and `config_print`.

## Dependencies And Integration Points
It is called early in `config_single`, before `config_find`, allowing the rest of the parser to operate only on the current schema. It integrates with backward-compatible output in `config_print_one`, which can also print historic names for selected settings.

## Risks And Test Signals
Risks include static buffer truncation if a mapped assignment grows beyond 100 bytes, missing aliases for old configs, and prefix mistakes because matching includes the equals sign but not full string tokenization beyond that. Signals are old `CONFIG` files parsing without unknown-key warnings and converted settings appearing under current names in output.
