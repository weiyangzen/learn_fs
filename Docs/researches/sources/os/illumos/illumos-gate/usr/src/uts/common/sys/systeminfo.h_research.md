# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systeminfo.h

## Purpose
Defines `sysinfo(2)` command constants, kernel backing string symbols, and host/domain/platform identifier limits.

## Main Interfaces
- Kernel symbols:
  - `architecture`
  - `architecture_32`
  - `hw_serial`
  - `hw_provider`
  - `srpc_domain`
  - `platform`
- UI-defined get commands:
  - `SI_SYSNAME`, `SI_HOSTNAME`, `SI_RELEASE`, `SI_VERSION`, `SI_MACHINE`, `SI_ARCHITECTURE`, `SI_HW_SERIAL`, `SI_HW_PROVIDER`, `SI_SRPC_DOMAIN`
- UI-defined set commands:
  - `SI_SET_HOSTNAME`, `SI_SET_SRPC_DOMAIN`
- illumos-defined get commands:
  - `SI_PLATFORM`, `SI_ISALIST`, `SI_DHCP_CACHE`, `SI_ARCHITECTURE_32`, `SI_ARCHITECTURE_64`, `SI_ARCHITECTURE_K`, `SI_ARCHITECTURE_NATIVE`, `SI_ADDRESS_WIDTH`
- Limits:
  - `HW_INVALID_HOSTID`
  - `HW_HOSTID_LEN`
  - `DOM_NM_LN`
- Userland declaration: `sysinfo(int, char *, long)`.

## Dependencies And Relationships
The command values are consumed by the `sysinfo(2)` syscall implementation and userland callers. The kernel symbols are filled by platform/boot code.

## Research Notes
The header documents the numeric allocation scheme for UI and illumos get/set commands. Existing command values are fixed due to historical registration/compatibility.
