# File Research: sources/local-fs/btrfs-progs/cmds/commands.h

## Purpose
Defines the internal command registration ABI for btrfs-progs CLI command handlers.

## Core Types
- `struct cmd_struct` stores token, callback, usage string array, optional subgroup, and flags.
- `struct cmd_group` stores group usage, group info text, and a null-terminated array of command pointers.

## Flags
Command flags include hidden commands, aliases, text/json output support, and global dry-run support. `CMD_FORMAT_MASK` covers output format flags.

## Macros
- `DEFINE_COMMAND()` creates a `cmd_struct_<name>` with explicit fields.
- `DEFINE_SIMPLE_COMMAND()` follows the `cmd_<name>` and `cmd_<name>_usage` naming convention.
- `DEFINE_COMMAND_WITH_FLAGS()` adds command-specific flags such as JSON support.
- `DEFINE_GROUP_COMMAND()` and `DEFINE_GROUP_COMMAND_TOKEN()` register command groups handled by `handle_command_group()`.

## Declared Commands
Declares top-level and inspect/filesystem helper commands, including `filesystem`, `filesystem_du`, `filesystem_usage`, `balance`, `device`, `inspect_dump_super`, `inspect_dump_tree`, and `inspect_tree_stats`.
