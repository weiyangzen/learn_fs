# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acl_impl.h

## Purpose

`acl_impl.h` defines the internal generic ACL container used by the public ACL API.

## Main Types

`acl_type_t` distinguishes `ACLENT_T` legacy ACL entries from `ACE_T` ACE entries.

`struct acl_info` stores the ACL type, entry count, per-entry size, flags, and pointer to the ACL entry array.

## Flags

`ACL_IS_TRIVIAL` marks ACLs equivalent to ordinary mode bits. `ACL_IS_DIR` marks directory ACL context. The comment notes that public ACL flags such as auto-inherit, protected, and defaulted may also be stored in the same flags field.

## Research Notes

This header is the narrow bridge between public `acl_t` handles and concrete ACL entry arrays. It is filesystem-relevant because VFS ACL calls must carry both legacy and ACE-style ACLs through one container.
