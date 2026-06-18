# File Research: sources/os/bsd/freebsd-src/sys/sys/extattr.h

## Purpose
Defines FreeBSD extended attribute namespaces and declares extended attribute syscalls or kernel credential checks.

## Main Interfaces
- Namespaces:
  - `EXTATTR_NAMESPACE_EMPTY`
  - `EXTATTR_NAMESPACE_USER`
  - `EXTATTR_NAMESPACE_SYSTEM`
- String names and `EXTATTR_NAMESPACE_NAMES` initializer macro.
- `EXTATTR_MAXNAMELEN`.
- Kernel API: `extattr_check_cred`.
- Userland APIs: `extattrctl`, `extattr_{delete,get,list,set}_{fd,file,link}`.

## Dependencies And Integration
Kernel mode operates on vnodes, credentials, threads, and access modes. Userland declarations expose the extattr syscall family.

## Risk Notes
Namespace numeric values are syscall ABI. Filesystems implementing extattrs must align their permission behavior with `extattr_check_cred`.
