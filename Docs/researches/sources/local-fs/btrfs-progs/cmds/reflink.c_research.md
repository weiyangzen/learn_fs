# File Research: sources/local-fs/btrfs-progs/cmds/reflink.c

## Purpose

Defines the `btrfs reflink` command group and a `reflink clone` subcommand intended for lightweight COW file copies/range cloning.

## Command Implemented

- `reflink clone [options] source target`

Documented options:

- `-s RANGESPEC`: range spec from source/same file semantics.
- `-t RANGESPEC`: range from target file, according to usage text.

Actual getopt string accepts `-r` and `-s`, not `-t`.

## Data Structures

- `struct reflink_range`
  - `from`
  - `length`
  - `to`
  - `same_file`
  - list node

## Key Helpers

- `parse_reflink_range()` parses `SRCOFF:LENGTH:DESTOFF`, accepting size suffixes through `arg_strtou64_with_suffix`.
- `reflink_apply_range()` is a stub returning `-EOPNOTSUPP`.

## Important Behavior and Status

This file appears incomplete:

- `reflink_apply_range()` does not perform cloning.
- `cmd_reflink_clone()` opens the source file but never opens the target file before checking `fd_target == -1`, so it always fails at target open validation.
- Usage text mentions `-t`, while getopt accepts `-r`.
- Range allocation and list cleanup are present, but successful reflink behavior is not implemented.

## Role in the Codebase

This is a command scaffold rather than a functional reflink implementation in the read version.
