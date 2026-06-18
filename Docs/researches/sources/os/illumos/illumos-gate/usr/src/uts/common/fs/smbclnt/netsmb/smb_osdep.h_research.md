# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_osdep.h

## Purpose
Provides small OS-compatibility definitions inherited from Apple/BSD-origin netsmb code so the illumos SMB client can use expected type names, allocation flags, user-address casts, Unicode conversion flags, and timespec helpers.

## Key Elements
Defines compatibility macros such as `PRIVSYM`, `min`, `CAST_DOWN`, `USER_ADDR_NULL`, and `CAST_USER_ADDR_T`. Provides BSD-style malloc flag names (`M_WAITOK`, `M_NOWAIT`, `M_ZERO`) and UTF/uconv flag constants. Declares `uconv_u8tou16` and aliases legacy integer/user pointer types such as `u_int64_t`, `user_addr_t`, `user_size_t`, and `c_caddr_t`.

The header also provides `timespeccmp`, `timespecadd`, and `timespecsub` macros and a fake-kernel `ddi_get_cred()` mapping.

## Dependencies
Depends on basic illumos integer, size, ssize, credential, and Unicode conversion types being available from surrounding includes.

## Behavior/Risks
This is compatibility glue, not protocol logic. Macro definitions can conflict with platform headers if included in the wrong order or if illumos headers later add equivalent definitions. The timespec arithmetic macros evaluate arguments multiple times and should be used only with simple lvalues.
