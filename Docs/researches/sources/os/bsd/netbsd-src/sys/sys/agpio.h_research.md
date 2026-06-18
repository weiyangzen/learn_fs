# File Research: sources/os/bsd/netbsd-src/sys/sys/agpio.h

Read completely: 150 lines.

Defines the AGP graphics aperture ioctl ABI.

Key elements:
- Fixes AGP GATT pages at 4096 bytes regardless of host page size.
- Provides AGP mode word extraction and insertion macros for request queue depth, ARQ size, calibration cycle, side-band addressing, AGP enable, 4G, fast writes, AGP 3 mode, and rate.
- Defines compatibility rate aliases for 1x/2x/4x.
- Defines ioctls for info, acquire, release, setup, allocate, deallocate, bind, and unbind.
- Disabled `#if 0` structs/ioctls show older reserve/protect region ideas.
- Public structs include `agp_version`, `agp_info`, `agp_setup`, `agp_allocate`, `agp_bind`, and `agp_unbind`.

Risks and notes:
- This is a user/kernel ioctl ABI; struct layout and ioctl numbers must remain stable.
- `AGP_MODE_SET_CAL` uses `__SHIFTIN((v), ~AGP_MODE_CAL)`, unlike the other setters that use the positive mask, which is a noteworthy macro risk.
