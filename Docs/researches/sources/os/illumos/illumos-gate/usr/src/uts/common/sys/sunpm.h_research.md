# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunpm.h

`sunpm.h` defines Sun-specific power-management interfaces used by kernel drivers. It includes DDI/devctl-related headers and is pulled into `sunddi.h`.

The header defines power-cycle transition check formats for SCSI and SMART devices. `pm_scsi_cycles` stores lifetime maximum cycles, current cycles, service date, and flags. `pm_smart_count` stores normalized allowed and consumed cycle counts. `pm_trans_data` tags the format and carries either structure.

It maps ACPI D-states to Solaris PM component levels: D3/off is level 0 and D0/full power is level 3, with generic property strings for `pm-components`. Kernel declarations include obsolete component creation/destruction/normal-power routines and active interfaces for busy/idle component accounting, current power query, power-change notification, transition checks, lower/raise power requests, and max-power updates.
