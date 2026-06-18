# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msdos.c

Common MS-DOS platform routines.

Key behavior:
- Uses `strerror` for OS error strings.
- Computes realtime from DOS date/time interrupts, using an epoch of January 1, 1980 and hundredths of seconds.
- Uses realtime as usertime approximation.
- Detects console files through DOS ioctl device-info bits.
- Provides no display environment variable.
- Defines scratch prefix `_temp_`, null device `nul`, and current directory `.`.

Notable dependencies:
- DOS register interface from `dos_.h`.

Research notes:
- Console detection has a special DLL behavior where `NULL` is considered console.
