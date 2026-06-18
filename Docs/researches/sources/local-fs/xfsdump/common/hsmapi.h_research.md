# File Research: sources/local-fs/xfsdump/common/hsmapi.h

## Summary
Declares the opaque HSM API used by xfsdump and xfsrestore to integrate with DMF-managed XFS files.

## Main Contents
- `HSM_API_VERSION_1`, the only supported API version.
- Opaque `hsm_fs_ctxt_t` and `hsm_f_ctxt_t` typedefs.
- Filesystem context lifecycle: `HsmInitFsysContext()`, `HsmDeleteFsysContext()`.
- File context lifecycle: `HsmAllocateFileContext()`, `HsmDeleteFileContext()`, `HsmInitFileContext()`.
- Dump-side estimators/modifiers: `HsmEstimateFileSpace()`, `HsmEstimateFileOffset()`, `HsmModifyInode()`, `HsmModifyExtentMap()`.
- Attribute filtering/addition hooks: `HsmFilterExistingAttribute()`, `HsmAddNewAttribute()`.
- Restore hooks: `HsmBeginRestoreFile()`, `HsmRestoreAttribute()`, `HsmEndRestoreFile()`.

## Intended Contract
Dump code can initialize one read-only filesystem context per mounted filesystem and one read-write file context per dump stream. Restore code does not need those contexts and uses only the restore hook trio.

The API lets xfsdump represent dual-residency HSM files as offline files with replacement HSM metadata, avoiding forced staging of file data during dump.

## Risks
The `HsmInitFileContext()` return-value comment in this header contradicts both `hsmapi.c` and callers: the implementation uses `0` for successful initialization and nonzero for “do not dump”.

The header intentionally hides context internals, so all callers must respect lifecycle and avoid stack assumptions except where implementation explicitly uses temporary internal contexts.

The API is versioned but only version 1 is supported.
