# sources/security-integrity/selinux/libselinux/include/selinux/avc.h

## Purpose
`avc.h` declares the userspace Access Vector Cache interface for object managers. It provides SID management, access checks, auditing, cache lifecycle, callbacks, statistics, netlink handling, and SELinux status-page helpers.

## Important APIs, types, and functions
Core types include `security_id_t`, `struct security_id`, `struct avc_entry_ref`, callback structs for memory/log/thread/lock behavior, `struct avc_cache_stats`, and event constants such as `AVC_CALLBACK_GRANT`. Key APIs include `avc_open()`, deprecated `avc_init()`, `avc_destroy()`, `avc_reset()`, `avc_cleanup()`, `avc_context_to_sid()`, `avc_sid_to_context()`, `avc_has_perm_noaudit()`, `avc_has_perm()`, `avc_audit()`, `avc_compute_create()`, `avc_compute_member()`, `avc_add_callback()`, statistics functions, `avc_netlink_*()`, and `selinux_status_*()`.

## Control flow
Callers initialize the cache with callbacks/options, convert security contexts to internal SIDs, check permissions against source/target SID/class/access vectors, optionally audit decisions, and respond to kernel policy-change events through netlink or status-page polling. Cache refs can be initialized with `avc_entry_ref_init()` and reused across repeated checks.

## State and persistence behavior
The AVC maintains in-process SID mappings, cached access vector decisions, callback registrations, statistics, and optional netlink/status mappings. It does not persist state across process lifetime. SID lifetime is reference-counted through deprecated `sidget()`/`sidput()` semantics and invalidated on destroy/reset paths.

## Dependencies and integration points
The header includes `selinux/selinux.h` for access vector types, decisions, options, and callbacks. It integrates with kernel SELinux policy services, userspace object managers, audit/log callbacks, threading/locking abstractions, and policy reload notifications.

## Risks and edge cases
Callers must initialize and destroy global AVC state in the right order, provide thread/lock callbacks when used concurrently, and handle `EACCES` versus other errors. Deprecated APIs remain for compatibility. Netlink FD ownership can be transferred to application event loops, so acquire/release pairing matters. Callback behavior affects logging and audit side effects.

## Test signals
Tests should cover init/open with default and custom callbacks, context/SID conversion, allow and deny permission checks, noaudit plus explicit audit flow, cache reset/statistics, callback registration events, netlink acquire/release/check paths, policy reload handling, and concurrent callers with lock callbacks.
