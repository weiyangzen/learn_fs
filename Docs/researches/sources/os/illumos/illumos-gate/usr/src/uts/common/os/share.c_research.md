# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/share.c

## Purpose

Implements vnode share reservations, including DOS/Windows-compatible deny modes, compatibility-mode semantics, cleanup by process or remote system ID, remote-share detection, and NBMAND share conflict checks for local/NFS/CIFS interoperability.

## Key Interfaces

- `add_share()` validates and adds a `shrlock` reservation to `vp->v_shrlocks` after checking conflicts.
- `del_share()` removes matching reservations and wakes waiters if an NBMAND share was removed.
- `cleanshares()` removes local shares for a process.
- `cleanshares_by_sysid()` removes remote shares for a system ID.
- `shr_has_remote_shares()` reports whether any remote share, or a share by a specific remote ID, exists.
- `nbl_share_conflict()` checks mandatory share reservations against read, write, read/write, remove, and rename operations.
- `proc_has_nbmand_share_on_vp()` reports whether a local process has an NBMAND share on a vnode.

## Matching and Semantics

- Share identity includes `s_sysid`, `s_pid`, owner length, and owner bytes for ordinary owner-specific operations.
- `is_match_for_del()` handles clustered and non-clustered NLM/PXFS delete matching cases.
- `is_match_for_has_remote()` handles clustered and non-clustered remote-share queries.
- `F_COMPAT` first-share behavior is special: compatibility-mode write/read cases are accepted or rejected according to historical DOS sharing semantics and read-only vnode checks.
- Simple non-compat conflicts are bitwise: requested access conflicting with existing deny, or requested deny conflicting with existing access, yields `EAGAIN`.

## Locking and Lifetime

- `vp->v_lock` protects the vnode share list.
- Added shares are deep-copied, including owner bytes.
- Deleted shares free owner, share, and list node allocations.
- Removing an NBMAND share broadcasts `vp->v_cv` for waiters such as blocking lock requests.
- `nbl_share_conflict()` asserts the caller is already inside the NBL critical section and then takes `v_lock` for list traversal.

## Dependencies

Uses vnode state, share/lock constants, NBMAND lock helpers, DTrace conflict probes, `vn_is_readonly()`, NLM sysid encoding macros, and caller context for remote/local operation identity.

## Notes for Future Work

- `add_share()` permits zero access only for remote systems for compatibility with older clients.
- `nbl_share_conflict()` intentionally skips mandatory share reservations owned by the same `(sysid, pid)` for I/O checks, but remove/rename conflict logic follows the documented mandatory-share algorithm.
