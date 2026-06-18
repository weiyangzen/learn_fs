# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/conf/autoconf.h

This header defines SCSI subsystem autoconfiguration knobs, probe result codes, reset/selection defaults, and kernel-global SCSI configuration variables.

Key definitions:
- `SCSI_DEBUG_*` flags distinguish target-driver, library, and host-adapter debug categories.
- `SCSI_OPTIONS_*` flags configure global SCSI behavior including linked commands, tagged queueing, disconnect/reconnect, synchronous transfer, parity, FAST/WIDE/FAST20/40/80/160/320, QAS, and maximum LUN limits.
- Documents `scsi_slave()` and `scsi_probe()` behavior and their return codes.
- Defines `SCSIPROBE_*` status values and an ASCII mapping macro.
- Defines defaults for reset delay and selection timeout.
- Defines `scsi_enumeration` flags for enabling dynamic enumeration and disabling target/LUN multithreading.
- Declares kernel globals: `scsi_options`, `scsi_enumeration`, `scsi_reset_delay`, `scsi_tag_age_limit`, `scsi_watchdog_tick`, `scsi_selection_timeout`, `scsi_host_id`, and `scsi_fm_capable`.

Dependencies:
- Pure SCSI configuration header, no direct includes in the file.
- Kernel variable declarations are gated by `_KERNEL`.

Impact:
- These flags shape SCSA bus probing, target enumeration, legacy parallel SCSI negotiation, and default timeout behavior.

Cautions:
- Comments describe historical SPI behavior and legacy probing paths; many options are meaningful primarily for parallel SCSI.
- Enumeration multithreading is explicitly tied to HBA locking robustness and buggy-HBA compatibility.
