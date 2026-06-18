# sources/user-network-fs/nfs-ganesha/src/include/config_parsing.h

## Purpose
`config_parsing.h` defines the public data model and helper macros for parsing Ganesha configuration files into typed C structures. It is the contract used by core config blocks, exports, FSAL modules, logging, recovery, and DBus update paths.

## Important APIs, Types, And Functions
Core opaque type `config_file_t` points at `struct config_root`. `enum term_type` describes lexer/parser terms; `enum config_type` describes target field types. `struct config_error_type` records categorized scan, parse, init, FSAL, uniqueness, validation, missing, deprecated, dispose, and internal errors plus a diagnostic memstream. `struct config_item_list` maps tokens to bit values. `struct config_item` describes one config parameter, with unions for booleans, strings/paths, IPs, integer ranges, FSIDs, lists/enums/tokens, boolbits, nested blocks, procedural handlers, and deprecated items. `struct config_block` wraps a top-level or nested block descriptor.

## Control Flow
Callers define static `config_item` arrays using `CONF_ITEM_*`, `CONF_MAND_*`, `CONF_RELAX_BLOCK`, `CONF_ITEM_BLOCK`, `CONF_ITEM_PROC_MULT`, and `CONFIG_EOL`. `config_ParseFile` builds a parse tree. `load_config_from_parse` walks matching blocks from the root, calls block `init`, validates and converts individual terms, then calls block `commit`. `load_config_from_node` does the same from a specific parse node. Error helpers classify whether accumulated errors are fatal, critical, harmless, or export-specific critical.

## State And Persistence
The parser owns an in-memory parse tree freed by `config_Free`. The parse root carries a generation number used by exports to track config updates. `config_error_type` can own a diagnostic buffer/memstream when initialized dynamically. Configuration persistence remains in the input file or URL; this API only transforms it into live process state.

## Dependencies And Integration Points
The header depends on standard C headers and is implemented by `config_parsing.c` plus lexer/parser files. It integrates with `support/exports.c` for export blocks, `FSAL/fsal_manager.c` for FSAL loading/configuration, logging config, recovery config, MDCACHE config, and FSAL-specific export blocks.

## Risks
The error-combining helpers treat the leading bitfield portion of `struct config_error_type` as a `uint16_t`, which is layout-sensitive and must be updated if the bitfield count grows. Offset macros depend on exact target structure/member names. `CONFIG_MARK_SET` writes bit masks through `set_off`, so incorrect offsets corrupt adjacent config state. Commit/init callbacks have nuanced ownership rules; returning allocated block memory or freeing it on errors must match parser expectations.

## Test Signals
Tests should parse valid and invalid config files, verify mandatory/unique/relaxed/deprecated handling, exercise all integer ranges and octal mode parsing, validate block init/commit/free paths, confirm diagnostic buffers, and verify export update generation behavior. Existing `config_parsing/test_parse.c` and `verif_syntax.c` are direct parser signals; export and FSAL startup tests provide integration coverage.
