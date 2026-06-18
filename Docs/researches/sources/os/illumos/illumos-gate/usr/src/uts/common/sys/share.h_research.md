# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/share.h

## Role

Defines file share reservation structures and kernel helpers for vnode share locking.

## Key Interfaces

- `MAX_SHR_OWNER_LEN` is 1024 bytes.
- `struct shr_locowner` identifies local owners by PID and ID.
- `struct shrlock` stores access mode, deny mode, system ID, PID, opaque owner length, and opaque owner pointer.
- `struct shrlocklist` links share locks.
- Kernel/fake-kernel helpers:
  - `add_share()`
  - `del_share()`
  - `cleanshares()`
  - `cleanshares_by_sysid()`
  - `shr_has_remote_shares()`
  - `proc_has_nbmand_share_on_vp()`

## Risk Notes

Share-lock owner matching depends on `s_sysid`, `s_pid`, `s_own_len`, and opaque owner data. Incorrect cleanup can leave stale local or remote share reservations on vnodes.
