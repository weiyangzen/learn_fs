# sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_functions.h

## Purpose

`nfs_proto_functions.h` declares all protocol service handlers, NFSv4 operation handlers, result free/copy helpers, async completion/resume hooks, pseudo filesystem operations, and NFSv4.1 slot cleanup.

## Important APIs, Types, and Functions

The header exports protocol descriptor arrays for enabled NFSv3, NFSv4, MOUNT, NLM, RQUOTA, and NFSACL. It declares service handlers for MOUNT, NLM, RQUOTA, NFSACL, NFS NULL, NFSv3 procedures, and `nfs4_Compound`. NFSv4 op handlers cover core v4.0, v4.1 sessions/pNFS, v4.2 operations, and v4.3 xattrs, with matching `*_Free` and selected `*_CopyRes` helpers. Additional APIs include `nfs_rpc_complete_async_request`, `drc_resume`, `compound_data_Free`, `get_nfs4_opcodes`, `xdr_COMPOUND4res_extended`, pseudo FS mount/unmount/prune helpers, and inline `release_slot`.

## Control Flow

Dispatch tables call protocol handlers through `nfs_function_desc_t`. NFSv4 compound dispatch maps opcodes to `nfs4_op_*`, handles async read/write/read-plus resume, frees each op result, and caches/copies selected results for NFSv4.1 replay. Pseudo FS helpers maintain export visibility during export load/reload.

## State and Persistence Behavior

Handlers mutate filesystem/export/session/state state through FSAL and SAL layers. Free functions own cleanup of result unions and cached compound references; `release_slot` releases a cached compound result and clears the slot pointer.

## Dependencies and Integration Points

It depends on NFS core, SAL data, and protocol data. It integrates with every protocol implementation file, duplicate request cache, async I/O, pseudo filesystem, NFSv4 session replay, pNFS, xattr support, and optional protocol builds.

## Risks and Test Signals

Risks include descriptor arrays not matching procedure counts, missing free routines for new ops, duplicated declarations hiding mismatches, async completion races, pseudo FS prune mistakes, and stale slot cached results. Tests should validate dispatch tables against constants, run every protocol op through decode/handler/free, exercise async read/write resume, NFSv4.1 replay/copy, pseudo export mount/unmount reload, and memory leak checks for all free paths.
