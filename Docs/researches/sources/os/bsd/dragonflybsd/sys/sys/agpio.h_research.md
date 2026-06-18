# File Research: sources/os/bsd/dragonflybsd/sys/sys/agpio.h

Read completely: 159 lines.

This header defines the AGP/GART ioctl interface.

Key contents:
- AGP page size constants.
- AGP mode word extract/set macros for request queue, ARQ size, calibration, sideband addressing, AGP enable, 64-bit GART, over-4G, fast writes, AGP 3 mode, and rate.
- Compatibility aliases for older mode names.
- Ioctls for info, acquire/release, setup, allocate/deallocate, bind/unbind, and chipset flush.
- Data structs for version, info, setup, allocation, bind, and unbind.

Security/reliability notes:
- No runtime logic. The ioctl structures are user/kernel ABI for graphics aperture management.
- Mode macros assume caller supplies valid bitfield values; they mask target fields but do not range-check inputs.
