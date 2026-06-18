# sources/user-network-fs/samba/source4/lib/registry/tools/regtree.c

## Purpose

`regtree.c` implements the `regtree` command, which recursively prints registry keys and optionally values from a local, remote, or file-backed registry.

## Important APIs, Types, and Functions

`print_tree()` recursively enumerates subkeys and values, prints key names or full paths, and touches security descriptors. `main()` parses `--file`, `--remote`, `--fullpath`, and `--no-values`, opens the selected backend, and starts traversal.

## Control Flow

In file mode, the command opens one imported hive key and prints it from `""`. In local or remote mode, it opens the registry context and iterates `reg_predefined_keys`, opening each available root and printing it. `print_tree()` prints indentation, enumerates subkeys by index, opens each subkey, recurses, then enumerates values and formats them through `reg_val_description()` unless values are disabled.

## State and Persistence Behavior

The command is read-only from a caller perspective. It allocates temporary talloc contexts for recursion and value/security descriptor retrieval. It does not persist output except to stdout and does not mutate registry data.

## Dependencies and Integration Points

It uses common registry open helpers, Samba command-line/credentials/loadparm setup, tevent, generic registry enumeration APIs, value formatting utilities, and security descriptor retrieval. It is built as `regtree` by `wscript_build`.

## Risks and Edge Cases

Recursive traversal has no cycle detection; unusual backend aliases or symbolic links could loop. Errors opening individual subkeys are silently skipped. Security descriptor retrieval errors are logged at debug level after traversal, and descriptors are not printed. Large registries can produce very large output and deep recursion.

## Test Signals

Smoke tests should run against a temp file hive and local Samba registry with and without `--fullpath` and `--no-values`, then assert key/value output ordering and formatting. Remote tests should verify skipped inaccessible predefined keys report useful stderr messages.

Source-read signal: reviewed complete local file (209 lines).
