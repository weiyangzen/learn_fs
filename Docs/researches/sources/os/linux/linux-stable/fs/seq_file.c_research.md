# File Research: sources/os/linux/linux-stable/fs/seq_file.c

## Purpose

Provides the generic `seq_file` framework used by procfs/debugfs/sysfs-like virtual files to expose sequential records safely through read, read_iter, lseek, formatting helpers, and standard list/hlist iterator helpers.

## Main Responsibilities

- Initializes and releases `struct seq_file`:
  - `seq_file_init()` creates the slab cache.
  - `seq_open()` allocates and attaches a `seq_file` to a file and records the sequence operation table.
  - `seq_release()` frees the dynamic buffer and seq_file object.
- Implements sequential read behavior:
  - `seq_read()` adapts legacy read into `seq_read_iter()`.
  - `seq_read_iter()` serializes with `m->lock`, preserves buffered remainder, grows buffers on overflow, advances sequence positions, and copies output to an iterator.
  - `traverse()` seeks to an arbitrary byte offset by replaying sequence output.
  - `seq_lseek()` supports `SEEK_SET` and `SEEK_CUR` by using `traverse()`.
- Provides formatting/output helpers:
  - `seq_printf()`, `seq_vprintf()`, optional `seq_bprintf()`, `seq_putc()`, `__seq_puts()`, `seq_write()`, `seq_pad()`, `seq_hex_dump()`.
  - Decimal and hex fast-path helpers: `seq_put_decimal_ull_width()`, `seq_put_decimal_ull()`, `seq_put_hex_ll()`, and `seq_put_decimal_ll()`.
  - `seq_escape_mem()` uses `string_escape_mem()` and `seq_commit()`.
- Provides path formatting helpers:
  - `mangle_path()` escapes selected characters.
  - `seq_path()`, `seq_file_path()`, `seq_path_root()`, and `seq_dentry()` print VFS paths into seq buffers.
- Provides single-record helpers:
  - `single_start()`, `single_open()`, `single_open_size()`, `single_release()`.
  - `seq_open_private()`, `__seq_open_private()`, and `seq_release_private()` manage per-open private data.
- Provides iterator helpers for lists, RCU lists, hlists, RCU hlists, and percpu hlist arrays.

## Key Data/Control Flow

- `seq_read_iter()` treats `m->count`/`m->from` as buffered output remaining from a prior read.
- If the caller reads from an offset that does not match `m->read_pos`, the file is replayed with `traverse()` to reconstruct the correct sequence position.
- Overflow is represented by setting `m->count = m->size`; readers detect it with `seq_has_overflowed()` and allocate a larger buffer.
- A positive return from `show()` means `SEQ_SKIP`; the produced record is discarded without treating it as an error.
- A buggy `next()` implementation that does not advance the position is rate-limited logged and compensated by incrementing `m->index`.

## Integration Notes

- Exports most helpers for filesystem and subsystem users.
- Uses `kvmalloc()` for sequence buffers so large virtual-file records can fall back to vmalloc.
- Relies on caller-provided `seq_operations` for locking of underlying data structures; this file serializes only per-open seq_file state.
- RCU iterator helpers require callers to hold the appropriate RCU read-side lock.

## Correctness and Risk Notes

- Buffer allocation rejects sizes over `MAX_RW_COUNT`.
- `seq_path_root()` returns `SEQ_SKIP` when the path is outside the supplied root.
- Several helpers set overflow state rather than returning immediate errors; callers should use `seq_has_overflowed()` or seq_file read retry behavior.
