# sources/user-network-fs/nfs-ganesha/src/config_parsing/config_parsing.c

## Purpose

`config_parsing.c` is the semantic loader for Ganesha configuration. It parses files into trees, reports diagnostics, converts parse nodes into typed C structures using `config_item` descriptors, loads nested blocks through callbacks, and provides query helpers for reload/update paths.

## Important APIs, Types, and Functions

Public APIs include `config_ParseFile`, `config_GetBlockNode`, `config_Print`, `config_Free`, `err_type_str`, `init_error_type`, `config_proc_error`, `report_config_errors`, `find_unused_blocks`, `get_parse_root`, `get_config_generation`, `get_parse_root_generation`, `find_config_nodes`, `load_config_from_node`, and `load_config_from_parse`. Important internals include `convert_bool`, `convert_number`, `convert_fsid`, `convert_list`, `convert_enum`, `convert_inet_addr`, `do_block_init`, `do_block_load`, `proc_block`, and expression parser/matcher helpers.

## Control Flow

`config_ParseFile` initializes parser state, calls the generated parser, records syntax/resource errors, cleans up scanner buffers, and returns the parse root. Semantic loading initializes defaults from a `config_item` table, searches matching statement/block nodes, checks mandatory and unique constraints, converts terminal values by type, processes lists/enums/bools/IPs/FSIDs, invokes custom processors, recursively loads child blocks, and calls optional check/commit/display callbacks. Top-level loading scans root blocks by name and handles default initialization when no block exists unless disabled.

## State and Persistence Behavior

The parse root owns tree memory and a generation counter incremented by the scanner. `config_error_type` owns an `open_memstream` diagnostics buffer until `report_config_errors` closes and frees it. Semantic loading mutates caller-provided or callback-allocated config structures, sets bit masks for `CONFIG_MARK_SET`, marks parse nodes as found for unknown detection, and may dispose of partially loaded blocks through init callbacks on error.

## Dependencies and Integration Points

It depends on the generated parser/scanner, `analyse.h`, public `config_parsing.h` descriptors, Ganesha logging/memory/list APIs, socket/address APIs, and FSAL ID conversion types. It is the common loader used by core NFS, FSAL, export, logging, RADOS URL, and reload configuration blocks.

## Risks and Edge Cases

The conversion path is broad and sensitive to descriptor metadata. Numeric conversion has separate signed/unsigned paths and supports `~` only for unsigned masks; diagnostics for invalid unsigned opcodes say "signed values". `find_unused_blocks` reports unknown blocks but does not increment `errors`. Expression parsing has a likely bug `if (!(isalpha(*sp) || *sp != '_'))`, which accepts many non-underscore non-alpha starts. IP defaults and conversion rely on `getaddrinfo` behavior and address-family fallback. Several paths use global parse block state and are not obviously concurrent-safe.

## Test Signals

Strong tests include descriptor-table unit tests for every `CONFIG_*` type, mandatory/unique/unknown handling, nested block init/check/commit rollback, default-only block loading, mark-set masks, deprecated parameter warnings, IP address parsing, FSID parsing, error aggregation, `find_config_nodes` expressions, and full sample config loads under sanitizers.
