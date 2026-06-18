# sources/test-tools/stress-ng/stress-ioport.c

Purpose: implements the x86 `ioport` stressor, exercising raw I/O port permissions and `inb`/`outb` transactions against selectable legacy ports such as POST `0x80`, VGA DAC red, and Bochs debug.

Important APIs/types/functions: `stress_ioport_opts_t` maps `in`, `out`, and `inout`; `stress_ioport_port_t` maps user-facing port names. `stress_ioport_supported()` probes `ioperm()`. `stress_ioport_ioperm()` verifies invalid `ioperm()` calls fail. The main loop uses `ioperm`, `inb`, `outb`, optional `/dev/port` `lseek`/`read`/`write`, and deprecated `iopl()` probes.

Control flow: the stressor reads option indexes, enables access to the selected port, optionally opens `/dev/port`, snapshots an initial byte, then sync-starts. Each iteration performs 32 reads and/or 32 writes depending on flags, pokes the same port through `/dev/port` when available, exercises invalid permission requests and `iopl` levels, increments bogo ops, and finally records nanoseconds per `inb` and `outb`.

State and persistence behavior: process I/O permission bits are enabled for one port and disabled on teardown. `/dev/port` writes can affect real hardware or emulated devices; the code restores only the sampled byte when using `/dev/port` and does not maintain persistent repo state.

Dependencies and integration points: gated to x86 builds with `sys/io.h` and I/O port support. Needs `CAP_SYS_RAWIO` or equivalent privilege. Registered as `CLASS_CPU` with always-on verification and option tables for stress-ng command parsing.

Risks: running on real hardware can have side effects because port I/O is not abstract. Permission failures are common and reported as skips in the support probe, but failures after option selection return stressor failure. Invalid `ioperm` tests assume failures; a permissive or unusual kernel could trip verification.

Test signals: verify skip behavior without raw I/O privilege, successful metrics with a safe VM port such as Bochs debug, and cleanup of `ioperm` permissions. Confirm invalid `ioperm` arguments do not unexpectedly succeed.
