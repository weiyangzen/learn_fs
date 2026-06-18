# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_pmf.c

## Purpose
Implements the kernel Power Management Framework (PMF): system/device suspend, resume, shutdown, device suspensor tracking, class helpers for network/input/display devices, generic PMF events, platform properties, sysctl debug controls, and workqueue initialization.

## Main Interfaces
- System operations: `pmf_system_suspend`, `pmf_system_resume`, `pmf_system_bus_resume`, `pmf_system_shutdown`.
- Platform properties: `pmf_set_platform`, `pmf_get_platform`.
- Device registration: `pmf_device_register1`, `pmf_device_deregister`, `pmf_self_suspensor_init`.
- Device transitions: `pmf_device_suspend`, `pmf_device_resume`, recursive/descendant/subtree suspend/resume/release helpers.
- Class helpers: `pmf_class_network_register`, `pmf_class_input_register`, `pmf_class_display_register`.
- Events: `pmf_event_inject`, `pmf_event_register`, `pmf_event_deregister`.
- `pmf_init`: initializes event pool, event/suspend workqueues, and idle display callout.

## Internal State And Dependencies
- Uses device framework internals (`device_pmf_*`, `deviter_*`, parent/active/enabled checks), workqueues, pools, proplib, callouts, sysctl, VFS sync calls, reboot/panic globals, and wsdisplay special handling.
- Tracks event handlers in `pmf_all_events`.
- Tracks display devices in `all_displays` and uses a global idle callout to emit display-off events.
- Defines standard suspensors: `system`, `drvctl`, and `self`, with qualifiers `PMF_Q_NONE`, `PMF_Q_DRVCTL`, `PMF_Q_SELF`.

## Control Flow Notes
- System suspend checks all devices have PMF support, blanks display if applicable, takes kernel lock, syncs buffers unless shutdown/panic already did, and suspends active devices leaves-first.
- System resume checks PMF support, resumes inactive enabled devices root-first, unlocks kernel, and restores display state.
- Device suspend records a suspensor at class/driver/bus levels, then calls class, driver, and bus suspend in that order.
- Device resume removes the suspensor; if other suspensors remain, it does nothing else. Otherwise it resumes bus, driver, then class.
- Recursive suspend descends to children before suspending the parent; recursive resume resumes ancestors before target.
- Generic events are delivered asynchronously by a workqueue to matching per-device or global handlers.

## Locking And Correctness
- Device PMF transitions acquire `device_pmf_lock` around per-device state.
- Suspensor arrays have fixed `DEVICE_SUSPENSORS_MAX` capacity and support delegator replacement/removal rules.
- Event handler list has no local lock in this file; correctness likely relies on PMF/device registration context or external serialization.
- Display idle list manipulation raises to `splsoftclock`.

## Risk Areas
- Suspend failure handling is incomplete at system level: comments note failures are printed but do not abort the overall suspend.
- Event injection can drop events if the pool allocation fails because it uses `PR_NOWAIT`.
- Multiple suspensors can keep a device logically suspended after one resume request.
- Network resume restarts interfaces only when `IFF_UP`.

## Filesystem Relevance
Moderate. PMF system suspend syncs buffers with `do_sys_sync`/`vfs_syncwait`, so it coordinates power transitions with filesystem writeback.
