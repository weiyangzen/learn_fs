# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priv.h

## Purpose
Defines the public and kernel-facing privilege API types, privilege syscall subcodes, implementation-info layout, per-credential flags, privilege-info records, special pseudo-privileges, and kernel helper routines.

## Main Interfaces
- Types:
  - `priv_chunk_t`
  - `priv_set_t`
  - kernel `priv_ptype_t`/`priv_t` as integers
  - userland `priv_ptype_t`/`priv_t` as strings
  - `priv_op_t`
- Syscall subcodes:
  - `PRIVSYS_SETPPRIV`
  - `PRIVSYS_GETPPRIV`
  - `PRIVSYS_GETIMPLINFO`
  - `PRIVSYS_SETPFLAGS`
  - `PRIVSYS_GETPFLAGS`
  - `PRIVSYS_ISSETUGID`
  - KLPD and pfexec register/unregister subcodes.
- Implementation layout:
  - `priv_impl_info_t`
  - `PRIV_IMPL_INFO_SIZE`
  - `PRIV_PRPRIV_INFO_OFFSET`
  - `PRIV_PRPRIV_SIZE`
- Credential flags:
  - `PRIV_DEBUG`, `PRIV_AWARE`, `PRIV_AWARE_INHERIT`
  - `NET_MAC_AWARE`, `NET_MAC_AWARE_INHERIT`
  - `PRIV_AWARE_RESET`, `PRIV_XPOLICY`, `PRIV_PFEXEC`
  - `PRIV_USER`
- Info records:
  - `priv_info_t`
  - `priv_info_uint_t`
  - `priv_info_set_t`
  - `priv_info_names_t`
  - `PRIV_INFO_SETNAMES`, `PRIV_INFO_PRIVNAMES`, `PRIV_INFO_BASICPRIVS`, `PRIV_INFO_FLAGS`
- Special pseudo-privileges:
  - `PRIV_ALL`, `PRIV_MULTIPLE`, `PRIV_NONE`, `PRIV_ALLZONE`, `PRIV_GLOBAL`
- Kernel APIs:
  - `/proc` conversion: `priv_prgetprivsize()`, `cred2prpriv()`, `priv_pr_spriv()`
  - implementation info: `priv_hold_implinfo()`, `priv_release_implinfo()`, `priv_get_implinfo_size()`
  - lookup: `priv_getset()`, `priv_getinfo()`, `priv_getbyname()`, `priv_getsetbyname()`, `priv_getbynum()`, `priv_getsetbynum()`
  - set operations: empty/fill/add/delete/member/equality/subset/intersect/union/inverse
  - credential permission and privilege-aware helpers
  - `setpflags()`, `getpflags()`

## Dependencies And Relationships
Includes `sys/types.h`, `sys/cred.h`, and generated/name constants from `sys/priv_names.h`. `priv_impl.h` defines the actual set representation for kernel/kmem consumers.

## Research Notes
The privilege implementation info is variable length and may be followed by additional typed records. Userland sees privileges by name while the kernel uses numeric IDs.
