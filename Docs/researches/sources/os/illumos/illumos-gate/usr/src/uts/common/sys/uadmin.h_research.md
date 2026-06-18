# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uadmin.h

## Purpose
Administrative reboot, shutdown, dump, suspend, remount, fast reboot, and boot-configuration command definitions.

## Main Interfaces
- Defines `uadmin` command values such as `A_REBOOT`, `A_SHUTDOWN`, `A_FREEZE`, `A_REMOUNT`, `A_DUMP`, `A_FTRACE`, `A_SWAPCTL`, `A_SDTTEST`, and `A_CONFIG`.
- Defines action values such as `AD_HALT`, `AD_BOOT`, `AD_IBOOT`, `AD_SBOOT`, `AD_SIBOOT`, `AD_POWEROFF`, `AD_NOSYNC`, `AD_FASTREBOOT`, and `AD_FASTREBOOT_DRYRUN`.
- Defines suspend/CPR actions including `AD_COMPRESS`, `AD_FORCE`, `AD_CHECK`, `AD_SUSPEND_TO_DISK`, `AD_SUSPEND_TO_RAM`, and reusable-state actions.
- Defines fast reboot SMF FMRI/property names and flags `UA_FASTREBOOT_DEFAULT` and `UA_FASTREBOOT_ONPANIC`.
- Kernel declarations include `mdboot`, `mdpreboot`, `kadmin`, and `killall`.
- User declaration exposes `uadmin(int, int, uintptr_t)`.

## Dependencies And Relationships
Includes `sys/types.h` and kernel-only `sys/cred.h`. Used by system administration tools, kernel reboot paths, crash dump handling, CPR, and boot configuration management.

## Research Notes
This header is command-number central for privileged system lifecycle operations; command/action combinations are interpreted in kernel administrative paths.
