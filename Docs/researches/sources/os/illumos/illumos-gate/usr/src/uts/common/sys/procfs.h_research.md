# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/procfs.h

## Purpose
Defines the structured `/proc` ABI for process/LWP control, status, psinfo, memory maps, credentials, privileges, watchpoints, I/O, resource usage, page data, fd info, core-file notes, and ILP32 compatibility structures.

## Main Interfaces
- Structured-proc selection:
  - `_STRUCTURED_PROC`
  - falls back to `sys/old_procfs.h` for non-kernel old-interface users.
- `/proc` control codes:
  - `PCNULL`, `PCSTOP`, `PCDSTOP`, `PCWSTOP`, `PCTWSTOP`, `PCRUN`
  - signal/fault/syscall tracing controls
  - register, watchpoint, agent, read/write, credential, privilege, zone controls.
- `PCRUN` flags:
  - `PRCSIG`, `PRCFAULT`, `PRSTEP`, `PRSABORT`, `PRSTOP`
- Status/info structures:
  - `lwpstatus_t`
  - `pstatus_t`
  - `lwpsinfo_t`
  - `psinfo_t`
- Flags/reasons:
  - `PR_STOPPED`, `PR_ISTOP`, `PR_DSTOP`, `PR_STEP`, `PR_ASLEEP`, `PR_AGENT`, process flags, and traced modes.
  - stop reasons `PR_REQUESTED`, `PR_SIGNALLED`, `PR_SYSENTRY`, `PR_SYSEXIT`, `PR_JOBCONTROL`, `PR_FAULTED`, `PR_SUSPENDED`, `PR_CHECKPOINT`
- Mapping structures:
  - `prmap_t`
  - `prxmap_t`
  - memory attribute flags `MA_READ`, `MA_WRITE`, `MA_EXEC`, `MA_SHARED`, `MA_ANON`, `MA_ISM`, `MA_NORESERVE`, `MA_SHM`
  - obsolete `MA_BREAK`, `MA_STACK`
- Credentials/privileges/security:
  - `prcred_t`
  - `prpriv_t`
  - `prsecflags_t`
- Watchpoint/I/O:
  - `prwatch_t`
  - `WA_READ`, `WA_WRITE`, `WA_EXEC`, `WA_TRAPAFTER`
  - `priovec_t`
- Usage/page data:
  - `prusage_t`
  - `prpageheader_t`
  - `prasmap_t`
  - `PG_REFERENCED`, `PG_MODIFIED`, `PG_HWMAPPED`
- File descriptor/core data:
  - `prfdinfo_core_t`
  - `prfdinfo_t`
  - `PRFDINFO_ROUNDUP`
  - `pr_misc_header_t`
  - `enum PR_MISC_TYPES`
  - socket option bit summaries in `prsockopts_bool_opts_t`
  - `prlwpname_t`
  - `prheader_t`
  - `prupanic_t`
  - `prcwd_t`
- Set manipulation macros:
  - `prfillset`
  - `premptyset`
  - `praddset`
  - `prdelset`
  - `prismember`
- 32-bit kernel views under `_SYSCALL32`:
  - `lwpstatus32_t`, `pstatus32_t`, `lwpsinfo32_t`, `psinfo32_t`
  - `prmap32_t`, `prxmap32_t`, `prcred32_t`, `prwatch32_t`, `priovec32_t`
  - `prusage32_t`, `prpageheader32_t`, `prasmap32_t`, `prheader32_t`

## Dependencies And Relationships
Includes feature tests, types, time, signal/siginfo, fault, syscall, pset, procfs ISA register layouts, privileges, stat, param, security flags, and thread name sizing. Closely mirrors state from `proc.h`, `priv.h`, and architecture-specific procfs headers.

## Research Notes
This is ABI-heavy. Many fields are reserved/filler for compatibility, and comments distinguish deprecated `psinfo` flags from structured status flags. Misc fd info uses self-describing variable-length records.
