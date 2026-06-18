# File Research: sources/os/bsd/freebsd-src/sys/sys/vdso.h

FreeBSD vDSO timekeeping and fast random-generation shared data header.

Key responsibilities:
- Defines `struct vdso_timehands` and `struct vdso_timekeep` for userland fast time reads, including algorithm, generation, scale, counter offset/mask, bintime offset, boottime, and machine-dependent fields.
- Defines busy/current/version and timehands algorithm constants.
- Defines `struct vdso_fxrng_generation_1`, asserts its size, and maps the current fxrng generation type/version constants.
- In userland, declares vDSO clock/gettimeofday/timecounter/timekeep helper entry points.
- Under `_KERNEL`, defines per-sysentvec timekeep state, declares optional fxrng seed generation push, timekeep push, native CPU/timecounter vDSO fill helpers, and `alloc_sv_tk()`.
- Under 32-bit compatibility, defines 32-bit bintime/timehands/timekeep structures and fill/allocation helpers.

Dependencies:
- Includes `sys/types.h` and `machine/vdso.h`; uses `struct bintime`, `clockid_t`, timecounter, and machine-dependent vDSO macros.

Notable risks:
- Generation counters and busy markers are concurrency ABI between kernel writers and userland readers.
- Native and compat32 layouts must match the consuming vDSO code exactly, including machine-dependent fields.
