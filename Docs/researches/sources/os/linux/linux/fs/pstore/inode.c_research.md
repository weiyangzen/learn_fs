# File Research: sources/os/linux/linux/fs/pstore/inode.c

## Role

Implements the `pstore` filesystem view. It creates a single-instance filesystem under `/sys/fs/pstore`, turns backend records into read-only files, supports unlink-based backend erasure, and handles mount option parsing.

## Filesystem Model

- `records_list` tracks created pstore files and their private records.
- `pstore_sb` tracks the mounted singleton superblock.
- `pstore_private` holds the dentry, record pointer, total visible size, and list linkage.
- Root directory mode is `0750`; record files are regular `0444`.

## Record File Operations

- `pstore_file_open()` uses seq operations for ftrace records and plain buffer reads for other record types.
- `pstore_file_read()` formats ftrace records via seq output; other types use `simple_read_from_buffer()`.
- `pstore_file_llseek()` dispatches to seq or default llseek as appropriate.
- `pstore_ftrace_seq_show()` decodes persistent ftrace records into human-readable CPU/timestamp/IP/function lines.

## Record Creation and Removal

- `pstore_mkfile()` rejects duplicate records for the same type/id/backend, allocates inode/dentry/private state, names files as `<type>-<backend>-<id>[.enc.z]`, sets timestamps, and links into `records_list`.
- `pstore_unlink()` removes the record from the in-memory list, calls backend `erase()` under the backend read mutex, and unlinks the file.
- `pstore_put_backend_records()` removes all files belonging to an unregistering backend.

## Mount Handling

- Parses `kmsg_bytes=<u32>`, historically ignoring unknown/invalid parameters.
- `pstore_reconfigure()` syncs the filesystem and updates global kmsg snapshot size.
- `pstore_fill_super()` initializes simple superblock state and immediately populates records from the active backend.
- `pstore_init_fs()` creates the sysfs mount point and registers the filesystem.

## Research Notes

This file is the pstore user-visible projection layer. Backend record buffers transfer ownership to `pstore_mkfile()` on success and are freed on failure or inode eviction.
