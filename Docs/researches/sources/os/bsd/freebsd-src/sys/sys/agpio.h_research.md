# File Research: sources/os/bsd/freebsd-src/sys/sys/agpio.h

AGP GART ioctl and mode definitions.

Key elements:
- Defines fixed AGP page size/shift.
- Provides AGP mode word get/set macros for rate, sideband addressing, fast writes, aperture request size, and related capabilities.
- Defines `AGPIOC_*` ioctl commands.
- Defines `agp_version`, `agp_info`, `agp_setup`, `agp_allocate`, `agp_bind`, and `agp_unbind`.

Dependencies:
- Requires ioctl macros and standard kernel/user types from including context.

Research notes:
- Hardware-memory aperture management ABI.
- Filesystem relevance is indirect through memory mapping and device infrastructure.
