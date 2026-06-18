# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/esunddi.h

## Role

`esunddi.h` declares private kernel DDI functions. It extends public `sunddi.h` with internal property manipulation, suspend/resume, memory locking, devinfo lookup/hold, branch dynamic reconfiguration, and driver-list compatibility routines.

## Property And Suspend/Resume Interfaces

- Declares property creation/modification/update functions for int, int64, arrays, strings, string arrays, and byte arrays.
- Declares property removal/undefine and property lookup functions (`e_ddi_getprop()`, `e_ddi_getprop_int64()`, `e_ddi_getproplen()`, `e_ddi_getlongprop()`, `e_ddi_getlongprop_buf()`).
- Declares `e_ddi_parental_suspend_resume()`, `e_ddi_resume()`, `e_ddi_suspend()`, and `pm_init()`.
- Exposes `pm_platform_power` as the platform power callback pointer.

## Device Reference And Memory Interfaces

- Defines `DEVI_REFERENCED` and `DEVI_NOT_REFERENCED` for `devi_stillreferenced()`.
- Declares `umem_lockmemory()`, a consolidation-private extended form of `ddi_umem_lock()` that can take callback ops and a process pointer.
- Defines `DDI_UMEMLOCK_LONGTERM`, used to reject long-term locks of shared regular-file mappings to avoid pvn deadlocks on truncation.
- Declares hold helpers by dev, path, and dip, including `E_DDI_HOLD_DEVI_NOATTACH`, plus a hold-count query.
- Declares major-instance path reconstruction and driver devinfo walking helpers.

## Branch And Callback Interfaces

- Defines branch flags such as `DEVI_BRANCH_CHILD`, `DEVI_BRANCH_CONFIGURE`, `DEVI_BRANCH_DESTROY`, `DEVI_BRANCH_EVENT`, `DEVI_BRANCH_PROM`, `DEVI_BRANCH_SID`, and `DEVI_BRANCH_ROOT`.
- Defines `devi_branch_t`, which carries an argument, callback, branch type, and PROM/SID creation function pointer.
- Declares branch create/configure/unconfigure/destroy/hold/release/reference operations.
- Keeps obsolete driver-list enter/tryenter/exit functions for compatibility.
- Defines `ddi_unbind_callback_t` and declares `e_ddi_register_unbind_callback()`.
