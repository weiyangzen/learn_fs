# sources/user-network-fs/samba/source4/lib/registry/tools/regshell.c

## Purpose

`regshell.c` implements an interactive registry shell for browsing and editing local, remote, or file-backed registry trees.

## Important APIs, Types, and Functions

`struct regshell_context` stores the registry context, current relative path, current predefined root name, current key, and root key. Commands include `ck/cd`, `info`, `list/ls`, `print`, `mkkey/mkdir`, `rmval/rm`, `rmkey/rmdir`, `pwd/pwk`, `set/update`, `predef`, `help`, and `exit/quit`. Important helpers are `get_full_path()`, `process_cmd()`, `reg_complete_command()`, `reg_complete_key()`, and `reg_completion()`.

## Control Flow

Startup parses `--file` and `--remote`, opens the selected backend, and chooses an initial key. File mode imports a hive and starts at that root; remote and local modes try predefined keys until one opens. The main loop builds a prompt from predef plus path, installs the current key for readline completion, reads a command line, parses it with `poptParseArgvString()`, dispatches to the command table, and updates the return status based on WERROR success.

## State and Persistence Behavior

The shell holds mutable current key/path state in memory. Commands can persistently set values, create keys, delete values, delete keys, and flush keys through the backend. `set` parses text data through `reg_string_to_val()`. `predef` changes the root to another predefined key. File-backed and local-backed changes persist via their hive backends; remote changes persist on the server.

## Dependencies and Integration Points

It depends on the registry library, common tool open helpers, Samba command-line/credentials/loadparm, tevent, readline abstraction `smb_readline`, NDR debug printing for security descriptors, and value conversion helpers. It is built as `regshell` with `SMBREADLINE` and `registry_common`.

## Risks and Edge Cases

`get_full_path()` mutates the supplied `path` through `strtok(discard_const_p(...))`, so passing immutable argv storage is risky. `process_cmd()` assumes `argv[0]` exists, so an empty parsed line can crash. Completion has off-by-one-looking `samelen` handling and uses a global `current_key` because readline cannot pass private data. `cmd_info()` returns success when security descriptor retrieval fails after printing an error, which may hide backend limitations. Text value parsing supports only selected types.

## Test Signals

Interactive tests should script navigation, path normalization with `.`, `..`, and absolute paths, setting and printing values, deleting keys/values, switching predefined roots, and command completion. Noninteractive smoke can pipe commands through readline-compatible input and inspect resulting registry state.

Source-read signal: reviewed complete local file (708 lines).
