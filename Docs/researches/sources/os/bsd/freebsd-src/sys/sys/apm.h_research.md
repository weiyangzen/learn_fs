# File Research: sources/os/bsd/freebsd-src/sys/sys/apm.h

Compatibility include wrapper.

Key elements:
- Public-domain file that includes `sys/disk/apm.h`.

Dependencies:
- `sys/disk/apm.h`.

Research notes:
- Keeps older include path `sys/apm.h` working while real disk partition definitions live under `sys/disk`.
