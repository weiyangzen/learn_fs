# File Research: sources/os/bsd/netbsd-src/sys/sys/rndio.h

Read completely: 173 lines.

This public random-subsystem ioctl header defines userspace-visible save/load, statistics, source description, source-control, and entropy-injection structures. Key types are `rndsave_t`, `rndpoolstat_t`, `rndsource_t`, `rndsource_est_t`, `rndstat_t`, `rndstat_est_t`, name-specific stat wrappers, `rndctl_t`, and `rnddata_t`.

It defines source flags such as collection/estimation controls, fast processing, callbacks, and enable hooks, plus source type IDs for disk, network, tty, hardware RNG, VM, power, and related sources. Ioctls include `RNDGETENTCNT`, source enumeration/name lookups, `RNDCTL`, `RNDADDDATA`, `RNDGETPOOLSTAT`, and entropy-estimate variants.

Risks: this is a privileged entropy-control ABI. `RNDADDDATA` includes caller-supplied entropy estimates, and source control flags can disable collection/estimation, so access control in the implementation is security-sensitive.
