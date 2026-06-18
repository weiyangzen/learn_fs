# File Research: sources/local-fs/xfsdump/common/hsmapi.c

## Summary
Implements xfsdump/xfsrestore support for SGI DMF/HSM metadata. It detects DMF-managed XFS files, treats dual-state/offline/partial files as offline for dump purposes, rewrites DMF attributes to a safe offline form, and protects files during restore with temporary `NOMIGR` attributes.

## Main Responsibilities
- Manage opaque filesystem and per-file HSM contexts.
- Interpret DMF root extended attribute `SGI_DMI_DMFATTR`.
- Read DMF attributes via `jdm_attr_multi()` using XFS/JDM file handles.
- Estimate dump size/offset for files whose online bytes should be represented as holes.
- Modify `xfs_bstat` and `getbmapx` data to make selected HSM files appear offline.
- Filter original DMF attributes and add replacement offline attributes to the dump stream.
- Add/remove temporary restore-time DMF attributes to prevent migration interference.

## Important Behavior
`HsmInitFsysContext()` supports only `HSM_API_VERSION_1`, allocates a DMF filesystem context, and stores a JDM filesystem handle for the mount point.

`HsmInitFileContext()` quickly rejects non-regular files, files without XFS attrs, and files without interesting DMAPI event bits. For candidates, it fetches `SGI_DMI_DMFATTR`, validates filesystem type, validates format 0 or format 1 length, reads the DMF state in big-endian form, and marks files in dualstate, unmigrating, partial, or offline states as dump candidates.

`HsmEstimateFileSpace()` returns zero bytes for candidate files when dumping dual-residency data as holes. It can use an existing file context, build a temporary accurate context, or use a cheaper bstat/event-bit heuristic.

`HsmEstimateFileOffset()` maps any requested byte quantity for a candidate file to EOF, because physical data is treated as absent.

`HsmModifyInode()` sets `bs_dmevmask` to the DMF event mask for candidate files. `HsmModifyExtentMap()` turns the remaining file range into one hole extent or indicates EOF.

`HsmFilterExistingAttribute()` skips the original DMF root attribute for candidate files so it can be replaced.

`HsmAddNewAttribute()` emits one replacement `SGI_DMI_DMFATTR`. It preserves format 1 only when a nonzero site tag requires it, otherwise writes format 0, and sets global state to offline. Format 1 output is reduced to one offline region spanning the whole file.

Restore helpers:
- `HsmBeginRestoreFile()` sets a temporary root DMF `NOMIGR` attr if the restored bstat appears DMF-managed.
- `HsmRestoreAttribute()` clears the temporary-removal flag when a real DMF attr is restored.
- `HsmEndRestoreFile()` removes the temporary attr if no real DMF attr replaced it.

## Dependencies
Depends on XFS bstat/getbmapx structures, XFS/JDM handles and attribute APIs, Linux attr APIs, UUID headers, and DMF attribute format knowledge copied into this file to avoid a DMAPI dependency.

## Risks
DMF attributes are parsed with fixed local structures and big-endian field helpers; incompatible future DMF formats are silently ignored.

`dmf_f_ctxt_t.attrval` is a fixed 5000-byte buffer assumed to exceed any possible DMF attribute value.

`HsmDeleteFsysContext()` frees only the context pointer; the JDM filesystem handle lifetime is not explicitly released in this file.

The cheap estimator assumes there are no MIG files and may under-estimate non-directory dump size when that assumption fails.

`HsmModifyInode()` returns success even for non-candidates, but only modifies candidates.

Restore protection is intentionally crude and state is carried by one integer flag, so correctness depends on the caller invoking begin/attribute/end hooks in order.
