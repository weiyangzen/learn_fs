# sources/test-tools/strace/src/linux/bfin/ioctls_arch0.h

Purpose: provides the `bfin` generated architecture ioctl table, with 11 initializer rows from asm/bfin_simple_timer.h, asm/bfin_sport.h, asm/ioctls.h; examples include BFIN_SIMPLE_TIMER_READ, BFIN_SIMPLE_TIMER_READ_COUNTER, BFIN_SIMPLE_TIMER_SET_MODE, BFIN_SIMPLE_TIMER_SET_PERIOD, BFIN_SIMPLE_TIMER_SET_WIDTH, BFIN_SIMPLE_TIMER_START.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE, _IOC_READ, _IOC_WRITE.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (12 lines).
