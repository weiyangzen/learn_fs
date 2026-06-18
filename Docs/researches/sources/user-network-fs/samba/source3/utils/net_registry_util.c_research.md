# sources/user-network-fs/samba/source3/utils/net_registry_util.c

## Purpose
This file provides shared output and path utility functions for local registry commands.

## Important APIs, Types, And Control Flow
`print_registry_key()` prints a key name and modification time, formatting NTTIME through Unix/http time helpers. `print_registry_value()` prints registry values in human or raw form for DWORD, SZ, EXPAND_SZ, MULTI_SZ, BINARY, and fallback unprintable types. It decodes strings with `pull_reg_sz()` and `pull_reg_multi_sz()`. `print_registry_value_with_name()` adds the value name and delegates formatting. `split_hive_key()` validates a path, converts legacy slash-only paths to backslashes, strips trailing backslashes, splits the hive name at the first backslash, and returns the hive/subkey strings.

## State And Persistence
The utilities do not persist data. They allocate temporary strings under caller/talloc contexts or `talloc_tos()` and print to the net command output stream.

## Dependencies And Integration Points
Dependencies include registry type definitions, `utils/net_registry_util.h`, `utils/net.h`, registry string conversion helpers, time conversion, and Samba talloc conventions. `net_registry.c` uses these functions for path opening and value/key display.

## Risks And Test Signals
Raw value mode suppresses labels but still prints one line per decoded MULTI_SZ element. Invalid string data simply stops printing that value payload. `split_hive_key()` converts `/` only when no backslash exists, so mixed separators are not normalized. Test hive-only paths, empty paths, trailing separators, slash-only legacy paths, mixed separators, DWORD too-short values, malformed SZ/MULTI_SZ blobs, binary values, and timestamp formatting.
