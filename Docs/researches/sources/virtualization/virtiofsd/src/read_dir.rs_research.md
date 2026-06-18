# File Research: sources/virtualization/virtiofsd/src/read_dir.rs

## Purpose

This file implements a Linux `getdents64(2)` based directory reader for virtiofsd. It adapts raw kernel `linux_dirent64` records into the crate’s `filesystem::DirectoryIterator` interface, yielding `filesystem::DirEntry` values with inode, offset, file type, and C-string name.

## Main Types And Functions

- `LinuxDirent64`: packed representation of the fixed-size prefix of Linux `struct linux_dirent64`.
- `ReadDir<P>`: buffered directory iterator over a caller-provided mutable byte buffer.
- `ReadDir::new(dir, offset, buf)`: seeks the directory file descriptor to a requested offset with `lseek64`, then fills the buffer through `new_no_seek`.
- `ReadDir::new_no_seek(dir, buf)`: unsafe constructor that calls `SYS_getdents64` at the descriptor’s current position without seeking.
- `ReadDir::remaining()`: returns unread bytes in the current buffer.
- `DirectoryIterator for ReadDir<P>`: parses one dirent at a time from the internal byte buffer.
- `strip_padding(b)`: converts padded kernel name bytes to a `CStr` by truncating after the first NUL.

## Control Flow

Construction either seeks first (`new`) or trusts the current descriptor position (`new_no_seek`). Both paths call Linux `getdents64` into the supplied buffer and set `current = 0`, `end = returned_byte_count`.

Iteration slices `buf[current..end]`, reads a `LinuxDirent64` from the front using `vm_memory::ByteValued::from_slice`, computes the name payload length from `d_reclen`, strips alignment padding, builds a `DirEntry`, then advances `current` by `d_reclen`.

## Integration Points

This module depends on:

- `crate::filesystem::{DirEntry, DirectoryIterator}` for the abstract directory iteration contract used by `server.rs` for FUSE `READDIR` and `READDIRPLUS`.
- `libc::SYS_getdents64`, `lseek64`, and Unix raw file descriptors.
- `vm_memory::ByteValued` to decode the packed dirent prefix from bytes.

The `seccomp.rs` allowlist includes `getdents64`, which is required by this reader.

## Important Invariants

- `new_no_seek` is unsafe because callers must ensure the directory FD position is valid and not concurrently manipulated.
- The parser trusts kernel-provided `d_reclen` and buffer layout, using debug assertions rather than runtime validation.
- `strip_padding` requires at least one NUL byte; missing NUL panics.
- Names returned as `&CStr` borrow from the internal buffer and are only valid until the iterator advances or is dropped.

## Tests

Unit tests cover `strip_padding` behavior for padded names, normal C strings, empty names, interior NUL truncation, and missing-NUL panic.

## Risks And Edge Cases

- Malformed buffers would panic or mis-parse, but the code explicitly trusts kernel output.
- Concurrent use of `new_no_seek` on the same descriptor can corrupt logical iteration because directory offsets are descriptor-global.
- `d_reclen` arithmetic assumes the record length is at least the fixed header size; this is only debug-checked.
