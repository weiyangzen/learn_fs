# File Research: sources/os/bsd/openbsd-src/sys/sys/errno.h

This header defines OpenBSD errno constants and kernel pseudo-errors.

Key definitions:
- Standard errno values from `EPERM` through `EPROTO`, with `ELAST` equal to 95 under `__BSD_VISIBLE`.
- Aliases: `EWOULDBLOCK` equals `EAGAIN`.
- BSD-visible errors include `ENOTBLK`, `ESOCKTNOSUPPORT`, `EPFNOSUPPORT`, `ESHUTDOWN`, `ETOOMANYREFS`, `EHOSTDOWN`, RPC/auth/IPsec/media-specific errors.
- Kernel pseudo-errors: `ERESTART` and `EJUSTRETURN`.

Behavior and integration:
- Includes `<sys/cdefs.h>` for feature visibility.
- Values are ABI-stable and used by libc, kernel syscall return handling, and applications.

Risk notes:
- `ELAST` must track the largest errno.
- Kernel pseudo-errors are internal negative values and must not escape as user-visible `errno`.
