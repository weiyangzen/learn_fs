# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_rrip.h

This header defines Rock Ridge Interchange Protocol support constants, byte-offset macros, and parser prototypes for HSFS.

Mount flags:
- HSFS-specific flags disable RRIP, trailing-dot handling, lowercase mapping, trailing-space handling, ISO version info, Joliet, Joliet truncation, ISO-9660:1999, or enable inode behavior for newer mkisofs images.
- `MS_NO_RRIP` is retained as a legacy generic mount flag but comments mark it as deprecated in favor of `HSFSMNT_NORRIP`.

RRIP identity:
- Version constants are all 1.
- Extension id is `"RRIP_1991A"`, with fixed descriptive/source strings.
- `IS_RRIP_IMPLEMENTED(fsp)` tests implementation state through SUSP extension bits.

Signatures:
- RRIP SUSP signatures include `CL`, `NM`, `PL`, `PN`, `PX`, `RE`, `RR`, `SL`, and `TF`.

Time fields:
- `TF` macros parse flags and locate creation, modification, access, and attribute timestamps.
- Time flags distinguish creation, modify, access, attributes, backup, expiration, effective, and long-time format.
- `IS_TIME_BIT_SET` must return 1 or 0 because offset macros sum bit-presence results.

POSIX metadata:
- `PX` macros parse mode, link count, uid, gid, and inode.
- `PN` macros parse major/minor device numbers.

Name and symlink handling:
- Name flags cover continuation, current, parent, root, volume root, and host.
- Higher-level parser flags record name changed and symlink complete states.
- Max supported RRIP filename length is 255.
- Symbolic-link macros parse SL fields and components.

Directory relocation:
- Defines child-link, parent-link, and relocated-directory flags.
- `CL` and `PL` macros parse child/parent LBNs.

Kernel parser API:
- Declares handlers for RRIP name, file attributes, device nodes, times, symlinks, parent/child links, relocated directories, Rock Ridge record, root-dir checking, and RRIP name copying.

Dependencies and relationships:
- Requires SUSP parsing context (`sig_args_t`) from `hsfs_susp.h`.
- Extends ISO/HSFS directory entries with POSIX semantics.
