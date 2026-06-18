# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acl.h

## Purpose

`acl.h` defines illumos ACL public types, permission bits, inheritance flags, syscall commands, userland ACL library interfaces, and kernel ACL comparison/sort hooks.

## Main Types

`aclent_t` is the POSIX-draft style ACL entry with type, uid/gid id, and permission mode. `ace_t` is the NFSv4/Windows-style access control entry with who, access mask, flags, and type. Kernel builds also define `ace_object_t` with object GUID fields.

## Constants

The file defines legacy ACL entry types and default ACL variants, ACE permission bits, ACE inheritance and identity flags, ACE allow/deny/audit/alarm types, ACL-level flags, CIFS-only ACE object/callback types, grouped permission masks, NFSv4-supported flags, and acl/facl command numbers for `aclent_t` and ACE ACLs.

## Userland Interfaces

Userland declarations include ACL validation, mode conversion, sorting, text conversion, allocation/free, path/fd get/set, trivial ACL checks, strip, and modern `acl_t` conversion APIs. The raw `acl()` and `facl()` syscalls are declared for all builds.

## Research Notes

This is a core filesystem security ABI header. It binds vnode security attributes, NFSv4 ACLs, CIFS semantics, and legacy UFS-style ACL tooling.
