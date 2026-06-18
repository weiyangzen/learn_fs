# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_fs_locks.c

## Role

`dump_fs_locks.c` reads and formats live or captured OCFS2 filesystem lock state from debugfs.

## Input Sources

It opens `/sys/kernel/debug/ocfs2/<uuid>/locking_state` unless a saved file path is supplied. It supports selected lockname filters, optional LVB dumping, and a busy-lock-only mode.

## Protocol Handling

The parser reads a hexadecimal protocol version up to `CURRENT_PROTO` 4, parses the base lock record, and, for protocol versions above 1, parses PR/EX wait and acquisition statistics.

## Output

For each selected lock resource it prints lock mode, lock flags, read/write holder counts, pending AST/unlock actions, requested/blocking modes, optional raw LVB bytes, decoded metadata LVBs for metadata locks, and timing statistics such as gets, failures, total waits, max/average wait, last wait, disk refreshes, and first wait.

## Risk Areas

The code silently skips additional unknown fields after the known record portion, which preserves forward compatibility for appended fields but not structural format changes. It depends on kernel internal lock constants mirrored in `ocfs2_internals.h`.
