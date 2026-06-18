# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ioctl.h

This header defines legacy System V/BSD ioctl constants and declares `ioctl`.

Key definitions:
- `IOCTYPE`, `LIOC*`, and `DIOC*` legacy command groups.
- Declares `extern int ioctl(int, int, ...);`
- Comment notes POSIX Issue 8 removed the old `<stropts.h>` placement and illumos exposes it here for portability.

BSD compatibility:
- Under `BSD_COMP`, includes `sys/ttychars.h`, `sys/ttydev.h`, and `sys/ttold.h`.
- Defines BSD terminal mode aliases such as `TANDEM`, `CBREAK`, `ECHO`, `RAW`, delay masks, erase modes, modem/control flags, etc.
- Includes `sys/filio.h` and `sys/sockio.h`.

Relevance:
- Core user/kernel control-plane ABI. Storage, filesystems, drivers, and network subsystems all rely on ioctl interfaces.
