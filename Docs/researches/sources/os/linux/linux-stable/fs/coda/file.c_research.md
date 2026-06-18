# File Research: sources/os/linux/linux-stable/fs/coda/file.c

## Purpose
Implements Coda regular-file operations by forwarding I/O and mmap to Venus-provided container files while notifying Venus of access intents and close/fsync events.

## Main Interfaces
- File I/O: `coda_file_read_iter()`, `coda_file_write_iter()`, `coda_file_splice_read()`.
- mmap handling: `coda_file_mmap()`, `coda_vm_open()`, `coda_vm_close()`.
- File lifecycle: `coda_open()`, `coda_release()`, `coda_fsync()`.
- Operation table: `coda_file_operations`.

## Control Flow
`coda_open()` allocates `coda_file_info`, converts Linux flags to Coda flags, calls `venus_open()` to obtain the underlying container file, propagates append/sync flags, and stores the container in `file->private_data`.

Read, write, and splice paths call `venus_access_intent()` before and after forwarding to the container file. Writes serialize on the Coda inode, forward through `vfs_iter_write()`, copy size/block metadata from the host inode, and update Coda inode mtime/ctime.

`coda_file_mmap()` verifies the container can be mmapped, sends a Venus mmap access intent, switches the Coda file and inode mapping to the host mapping under `c_lock`, tracks mapping counts, then invokes `vfs_mmap()` on the host file. It wraps host vm operations so Coda can hold a reference to the original Coda file until the final VMA close.

`coda_release()` sends `venus_close()`, unwinds mmap mapping counts, restores the Coda inode mapping when no mappings remain, drops the container file, and frees private data. `coda_fsync()` writes back the Coda mapping, fsyncs the container file, and sends `venus_fsync()` for full syncs.

## State And Synchronization
`struct coda_file_info` tracks the host file, mmap count, and whether Venus supports access intents. `struct coda_vm_ops` wraps host vm ops with refcounting. `c_lock` protects inode/file mmap counters and mapping substitution.

## Integration Points
Bridges VFS file operations to Venus cache/container files, access-intent upcalls, fsync upcalls, and Coda inode metadata.

## Risks And Review Focus
- Mapping substitution between Coda inode mapping and host inode mapping is delicate and returns `-EBUSY` if the container changes under active mappings.
- Access-intent finish calls run even after failed start operations; Venus-side support flags must tolerate that protocol.
- Release return values are ignored by VFS, so close errors cannot be surfaced through `release()`.
