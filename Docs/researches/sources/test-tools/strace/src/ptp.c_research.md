# sources/test-tools/strace/src/ptp.c

Purpose: Decodes PTP clock ioctls and their nested time/capability/request structures.

Important APIs/types/functions: `ptp_ioctl`; helpers `print_ptp_clock_time`, array-member callbacks, and `PRINT_RSV` for nonzero reserved arrays.

Control flow: dispatches by ioctl code. Getter ioctls often print input fields on entry and output arrays on exit, skipping output on `syserror`. It decodes caps, external timestamp requests, periodic output requests, PPS enable, system offset sample arrays, pin function get/set, precise/extended offsets, and reserved fields for v2/cycles variants.

State and persistence: stateless; syscall phase determines whether to fetch input or output structures.

Dependencies/integration: `<linux/ptp_clock.h>`, ioctl size checks, xlat tables for flags/functions, `clocknames`, `sprinttime_nsec`, and ioctl dispatch from the generic ioctl decoder.

Risks: struct size assertions must track kernel headers. Output array lengths are bounded with `MIN(n_samples, PTP_MAX_SAMPLES)`. Some unions change meaning based on flags (`phase` vs `start`, `on` vs reserved), so flag handling is critical.

Test signals: PTP ioctl tests for all request variants, get/set phase differences, reserved nonzero fields, failed getters, and precise/extended sample output.
