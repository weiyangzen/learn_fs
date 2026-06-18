# sources/storage-engines/wiredtiger/src/config/config_ext.c

## Purpose

`config_ext.c` exposes WiredTiger configuration helpers through the extension API. It adapts external `WT_EXTENSION_API` calls to the internal configuration parser by resolving the caller's `WT_SESSION` to a `WT_SESSION_IMPL`, falling back to the connection default session when extensions call without an explicit session.

## Important APIs, Types, and Functions

- `__wt_ext_config_get`: external wrapper for looking up a key in a NULL-terminated configuration stack represented as `WT_CONFIG_ARG`.
- `__wt_ext_config_get_string`: external wrapper for looking up a key in one configuration string.
- `__wt_ext_config_parser_open`: exposes `wiredtiger_config_parser_open` to extensions for a raw configuration string and length.
- `__wt_ext_config_parser_open_arg`: opens a parser over the last non-NULL entry in a configuration stack.
- Key types are `WT_EXTENSION_API`, `WT_SESSION`, `WT_CONFIG_ARG`, `WT_CONFIG_ITEM`, and `WT_CONFIG_PARSER`.

## Control Flow

The lookup wrappers cast `wt_api->conn` to `WT_CONNECTION_IMPL`, cast the optional `WT_SESSION` to `WT_SESSION_IMPL`, and default to `conn->default_session` when the argument is NULL. `__wt_ext_config_get` returns `WT_NOTFOUND` for a NULL config stack, otherwise calls `__wt_config_gets`. `__wt_ext_config_get_string` directly calls `__wt_config_getones`. Parser-open wrappers either pass the raw string through or scan the config stack to the final entry and parse only that entry.

## State and Persistence Behavior

This file does not persist state. It reads configuration strings supplied by callers and returns parsed values or parser handles. The only connection state it depends on is `default_session`, used to route error handling and memory context when no session was provided.

## Dependencies and Integration Points

The file depends on `wt_internal.h`, internal config APIs such as `__wt_config_gets` and `__wt_config_getones`, and the public parser function `wiredtiger_config_parser_open`. It is wired into the extension API from `conn_api.c` through `__conn_get_extension_api`, which assigns these functions to `WT_EXTENSION_API.config_get`, `config_get_string`, `config_parser_open`, and `config_parser_open_arg`.

## Risks and Edge Cases

- `WT_CONFIG_ARG` is treated as `const char **`; callers must pass a valid NULL-terminated config stack.
- `config_parser_open_arg` intentionally parses only the final stack entry, not the merged view. Extensions needing effective value lookup should use `config_get`.
- Falling back to `default_session` is convenient but means extension calls without a session share the default session's error and scratch context.
- A NULL or empty config stack opens a parser with `p = NULL` and `len = 0`, relying on `wiredtiger_config_parser_open` to handle the empty stream.

## Test Signals

Coverage is indirect through extension tests that call `WT_EXTENSION_API` config helpers, parser tests for `wiredtiger_config_parser_open`, and integration paths that load collators, compressors, encryptors, storage sources, or file systems with extension configuration. Useful test signals include `WT_NOTFOUND` on NULL stacks, correct override behavior for stack lookups, and parser behavior for the last config string in a stack.
