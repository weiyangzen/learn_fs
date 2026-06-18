# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/epm.h

## Role

`epm.h` is an internal kernel power-management header. It defines the device power-management state carried in `dev_info_t`, PM component metadata, PM dependency work, platform power request payloads, scan/threshold state, debug controls, locking macros, and the internal PM function surface used by kernel PM implementation files and private DDI code.

## Device And Component State

- Declares `e_pm_props()` and `e_new_pm_props()` for parsing PM-related device properties.
- Defines special power-level request values `PM_LEVEL_UPONLY`, `PM_LEVEL_DOWNONLY`, and `PM_LEVEL_EXACT`.
- Defines `devi_pm_flags` bits such as `PMC_NEEDS_SR`, `PMC_NO_SR`, `PMC_PARENTAL_SR`, `PMC_WANTS_NOTIFY`, `PMC_BC`, component parse state bits, threshold source bits, `PMC_NOPMKID`, `PMC_NO_INVOL`, `PMC_VOLPMD`, `PMC_SKIP_BRINGUP`, `PMC_CONSOLE_FB`, `PMC_DRIVER_REMOVED`, `PMC_CPU_DEVICE`, and `PMC_CPU_THRESH`.
- Defines scan bookkeeping with `pm_scan_t`, scan flags (`PM_SCANNING`, `PM_SCAN_AGAIN`, `PM_SCAN_STOP`, `PM_SCAN_DISPATCHED`), and default/CPU scan intervals.
- Defines `pm_comp_t` for parsed `pm-components` property data and `pm_component_t` for live component power/busy/timestamp/normal-current-level state.
- Defines `pm_info_t`, stored on devices that participate in PM, carrying PM state bits, direct-PM clone owner, inline power-level storage, optional level pointer, and direct-PM condition variable.

## Dependencies And Platform Requests

- Defines `pm_dep_wk_t` and dependency work types for power-on/off, attach/detach, dependency removal, bringup, keeper/kept processing, and CPR suspend/resume.
- Defines `pm_canblock_t` to distinguish blocking, failing, or bypassing when user/controller action might be needed.
- Defines `pm_cpupm_t` CPU PM modes: not set, polling, event-driven, and disabled.
- Defines the binary-compatibility-sensitive `pm_request_type` enum and `power_req_t` union used for parent/PPM power requests. Request variants cover set power, suspend/resume, pre/post notifications, PPM configuration, all-lowest notifications, lock/unlock/try-lock, power lock owner queries, ACPI S-state entry, and list search.
- Defines S3/S4 support constants, `s3a_t`, and test-point values for suspend-to-RAM paths.
- Defines bus power operation payloads for child power changes, nexus power-up, `power_has_changed`, and no-involuntary-power bookkeeping.

## PM Records, Macros, And Debugging

- Defines dependency records (`pm_pdr_t`), threshold records (`pm_thresh_rec_t`/`pm_pte_t`), PM direct/detaching state bits, and many access macros such as `PM_GET_PM_INFO()`, `PM_GET_PM_SCAN()`, `PM_CP()`, `PM_ISDIRECT()`, `PM_ISBC()`, `PM_ISCPU()`, and CPU PM mode predicates.
- Defines `PM_SCANABLE()` to express the combined autopm/CPU-PM scan policy.
- Provides PM device name formatting macros and extensive DEBUG-only `PMD_*` bit flags with `PMD()` logging through `pm_log()`.
- Provides POST/debug progress codes `PT_*` for suspend/resume paths.
- Defines power and devinfo locking wrappers: `PM_LOCK_DIP()`, `PM_UNLOCK_DIP()`, `PM_LOCK_BUSY()`, `PM_LOCK_POWER()`, `PM_TRY_LOCK_POWER()`, and related helpers.

## Internal Function Surface

The header declares the internal PM implementation API: detach/failure handling, `pm_power()`, `pm_unmanage()`, normal-power queries, threshold setting, power locking, bus ctlops, child init/uninit, all-to-normal, set-power, scan setup/stop/rescan, config/probe/attach/detach notifications, bus power dispatch, hold/release, driver removal, CPR no-invol reattach, direct-level save/restore, dependency-thread dispatch, PPM registration, and console-framebuffer helpers.

## Filesystem/OS Relevance

Although not filesystem-specific, this header affects VFS and device behavior through suspend/resume, direct PM, dependency bringup, devinfo state, and bus power operations for storage and display devices.
