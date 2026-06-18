# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_acl.h

## Role

Defines UFS ACL on-disk and in-core structures, shadow-inode ACL cache state, filesystem-security-data records, validation flags, and helper macros for mode/ACL conversion.

## Key Structures

- `ufs_acl_t` is the on-disk ACL record with tag/legacy next-field union, permission bits, and user/group ID.
- `ufs_ic_acl_t` is an in-core linked-list ACL entry.
- `ufs_aclmask_t` records whether a mask is present and the mask bits.
- `ic_acl_t` groups owner, group, other, named users, named groups, and mask entries.
- `si_t` tracks cached shadow inode ACL state, hash/list links, flags, shadow inode number, device, signature, on-disk use count, in-core reference count, lock, access ACL, and default ACL.
- `ufs_fsd_t` is a typed on-disk filesystem-security-data record.

## Macros and Semantics

Defines FSD record types (`FSD_ACL`, `FSD_DFACL`, reserved slots), alignment helpers (`FSD_TPSZ`, `FSD_TPMSK`, `FSD_RECSZ`), validation flags, `CHECK_ACL_ALLOWED()`, `MASK2MODE()`, `MODE2ACL()`, and `ACL_MOVE()`.

## Risk Notes

ACL mode masking affects `getattr`, access checks, and shadow-inode persistence. Record alignment is explicit; all FSD walking must use `FSD_RECSZ()` rather than raw byte lengths.
