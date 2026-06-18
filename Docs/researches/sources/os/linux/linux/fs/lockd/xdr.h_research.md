# File Research: sources/os/linux/linux/fs/lockd/xdr.h

## Purpose
`xdr.h` defines legacy lockd/NLM XDR-facing constants, structures, status aliases, and function prototypes used by the v1/v3 server procedure implementation.

## Main Responsibilities
- Defines NSM and NLM string/private-data size constants.
- Defines Linux's NLM cookie size limit.
- Provides big-endian status aliases such as `nlm_granted`, `nlm_lck_denied`, and `nlm_lck_denied_grace_period`.
- Defines `struct nlm_lock`, `struct nlm_cookie`, `struct nlm_args`, `struct nlm_res`, and `struct nlm_reboot`.
- Declares legacy server XDR decode and encode functions implemented in `xdr.c`.

## Key Structures
- `nlm_lock`: caller name, file handle, owner handle, svid, original lock range fields, and embedded VFS `file_lock`.
- `nlm_cookie`: fixed 32-byte storage plus length.
- `nlm_args`: common argument carrier for lock/share/notify operations.
- `nlm_res`: common response carrier with cookie, status, and optional lock.
- `nlm_reboot`: statd reboot notification payload.

## Integration Points
- Included throughout lockd server/client paths that use legacy NLM types.
- Paired with `svcxdr.h` and `xdr.c` for actual serialization.
- Shares `struct file_lock`, NFS file handle, and SUNRPC XDR types.

## Risks and Edge Cases
- The header documents that the protocol allows larger cookies than Linux stores.
- `nlm_lock` contains both protocol range fields and VFS-normalized range state; callers must keep the intended representation clear.
