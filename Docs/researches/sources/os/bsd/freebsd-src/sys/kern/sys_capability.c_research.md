# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_capability.c

## Purpose

Implements FreeBSD Capsicum capability mode and file-descriptor capability rights enforcement syscalls. It provides process sandbox entry/query and descriptor rights limiting/querying for general rights, ioctl command subsets, and fcntl command subsets.

## Main responsibilities

- Enter/query Capsicum capability mode:
  - `sys_cap_enter()`
  - `sys_cap_getmode()`
- Check descriptor rights:
  - `cap_check()`
  - `cap_check_failed_notcapable()`
- Convert mmap rights to VM protection:
  - `cap_rights_to_vmprot()`
- Limit and query file descriptor rights:
  - `kern_cap_rights_limit()`
  - `sys_cap_rights_limit()`
  - `sys___cap_rights_get()`
- Limit and query ioctl command rights:
  - `cap_ioctl_check()`
  - `kern_cap_ioctls_limit()`
  - `sys_cap_ioctls_limit()`
  - `sys_cap_ioctls_get()`
- Limit and query fcntl command rights:
  - `cap_fcntl_check_fde()`
  - `cap_fcntl_check()`
  - `sys_cap_fcntls_limit()`
  - `sys_cap_fcntls_get()`

## Compile-time modes

- With `CAPABILITY_MODE`, process credentials can be marked with `CRED_FLAG_CAPMODE`.
- Without `CAPABILITY_MODE`, cap mode syscalls return `ENOSYS`.
- With `CAPABILITIES`, descriptor rights limiting and checking is active.
- Without `CAPABILITIES`, capability descriptor syscalls return `ENOSYS`.

## Important control flow

- `sys_cap_enter()` creates/copies credentials, sets `CRED_FLAG_CAPMODE`, swaps process credentials under `PROC_LOCK`, and frees the old credential.
- `_cap_check()` verifies requested rights are contained in held rights and optionally emits ktrace capability-failure records.
- `kern_cap_rights_limit()` requires the requested rights to be a subset of current rights, updates `fde_rights`, clears ioctl/fcntl filters if the corresponding general right is removed, and uses `seqc_write_begin/end`.
- `sys_cap_rights_limit()` copies in versioned rights safely, validates version and rights shape, normalizes old version bits, audits, and delegates to the kernel helper.
- `sys___cap_rights_get()` copies current rights out, rejecting old-version requests if unknown higher-version rights are present.
- `kern_cap_ioctls_limit()` replaces an fd's allowed ioctl list only if it is a subset of the old list.
- `sys_cap_ioctls_get()` returns either a copied command list or `CAP_IOCTLS_ALL`.
- `sys_cap_fcntls_limit()` restricts fcntl rights by subset only.

## Filesystem/storage relevance

Capsicum controls what file descriptors may do. This affects VFS and filesystem operations by gating read, write, mmap, ioctl, fcntl, truncate, event polling, and similar descriptor operations at the fd layer. Filesystem code typically sees already-authorized operations, while this file enforces descriptor delegation boundaries.

## Edge cases and safeguards

- Capability rights can only be reduced, not expanded.
- ioctl list length is capped by `IOCTLS_MAX_COUNT`.
- Versioned rights copyin checks detect races or malformed user rights.
- Descriptor updates occur under filedesc locks and seqc write sections.
- Capability failure tracing integrates with ktrace.
- `trap_enotcap` sysctl controls SIGTRAP delivery behavior for `ECAPMODE`/`ENOTCAPABLE`.

## Research notes

Classify as security/sandbox descriptor-rights infrastructure. It is important context for syscall files such as `sys_generic.c`, which calls `fget_*()` with specific capability rights for read/write/ioctl/poll paths.
