# File Research: sources/os/linux/linux/fs/proc/util.c

## Scope

This file provides a small proc utility for parsing decimal dentry names.

## Public And Internal APIs Covered

- `name_to_int()`.

## Control Flow And Behavior

- `name_to_int()` converts a `struct qstr` to an unsigned integer.
- It rejects multi-character numbers with a leading zero, non-decimal characters, and values that would overflow the unsigned range.
- On failure it returns `~0U`; on success it returns the parsed value.

## Dependencies And Risks

- Used by proc PID-style lookup paths that need fast numeric name parsing.
- `~0U` is the sentinel, so valid callers must treat that value as invalid rather than a legitimate parsed ID.
