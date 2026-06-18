<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_gpfs.c -->
# sources/user-network-fs/samba/source3/modules/test_vfs_gpfs.c

## Purpose
This cmocka unit test covers pure mapping helpers in Samba's GPFS VFS module. It validates translation between Samba share-access and DOS attribute bits and the GPFS deny/lease/winattr constants used when integrating with GPFS-specific file APIs.

## Important APIs, Types, And Functions
The test includes `vfs_gpfs.c` directly. `test_share_deny_mapping` checks `vfs_gpfs_share_access_to_deny` for all meaningful combinations of `FILE_SHARE_READ`, `FILE_SHARE_WRITE`, and `FILE_SHARE_DELETE`. When `HAVE_KERNEL_OPLOCKS_LINUX` is defined, `test_gpfs_lease_mapping` checks `lease_type_to_gpfs` for `F_RDLCK`, `F_WRLCK`, and `F_UNLCK`. The DOS attribute tests validate `vfs_gpfs_winattrs_to_dosmode` and `vfs_gpfs_dosmode_to_winattrs`.

## Control Flow
`main` assembles the conditional cmocka test list and runs it with subunit output. Each test is table-like but expressed as direct assertions against expected bit masks.

## State And Persistence
No GPFS filesystem, TDB, xattr, or share state is mutated. The tests exercise in-process mapping functions only.

## Dependencies And Integration Points
Dependencies include cmocka, Samba DOS/share constants, GPFS constants from the included implementation, and optional Linux kernel oplock support. These helpers are integration points between Samba's SMB protocol semantics and GPFS kernel/library semantics for share denies, leases, and Windows attributes.

## Risks
The test encodes the GPFS limitation that Samba cannot express "deny delete only" and therefore maps `FILE_SHARE_READ|FILE_SHARE_WRITE` to zero deny bits. It does not cover real GPFS ioctl behavior, error paths, fileset handling, or lease lifecycle.

## Test Signals
Passing tests indicate GPFS bit translations remain stable. Failures are high-signal for accidental constant changes, wrong bitwise inversion of share modes, or DOS attribute translation regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_gpfs.c -->
