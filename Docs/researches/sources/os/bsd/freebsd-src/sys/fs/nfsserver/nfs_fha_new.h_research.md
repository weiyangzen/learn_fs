# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_fha_new.h

## Purpose
Declares the public data structures, defaults, constants, and entry points for the FreeBSD NFS server File Handle Affinity scheduler implemented in `nfs_fha_new.c`.

## Main Definitions
- `FHANEW_SERVER_NAME` sets the server name to `nfsd`.
- Default sysctl values enable FHA, read locality, and write locality; set bin shift to 22 bytes of locality distance; cap default threads per file handle at 8; and leave per-thread request limit unlimited.
- `FHA_HASH_SIZE` is 251 hash buckets.
- `struct fha_ctls` stores runtime tuning knobs.
- `struct fha_hash_entry` tracks one file-handle affinity key, shared/exclusive operation counts, associated service-thread list, and its protecting mutex.
- `struct fha_hash_slot` contains a list of entries and a mutex.
- `struct fha_info` carries extracted per-request affinity data: file-handle key, offset, lock type, read flag, and write flag.
- `struct fha_params` contains the hash table and server name.
- Declares `fhanew_assign()` and `fhanew_nd_complete()` for RPC server integration.

## Integration
Included by the NFS server FHA implementation and RPC/NFS server code that delegates service-thread choice and completion accounting to FHA.

## Risks
- Constants directly shape scheduler behavior and memory footprint; changing hash size or defaults affects contention and locality globally.
- `struct fha_hash_entry` embeds an RPC service-thread list, so thread lifecycle and completion accounting must match the implementation's expectations.
