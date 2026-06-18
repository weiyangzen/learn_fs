# sources/test-tools/stress-ng/stress-lsm.c

Purpose: implements `lsm`, a Linux security-module syscall stressor. It exercises `lsm_list_modules`, `lsm_get_self_attr`, and negative `lsm_set_self_attr` cases.

Important APIs/types/functions: shim wrappers call `__NR_lsm_list_modules`, `__NR_lsm_get_self_attr`, and `__NR_lsm_set_self_attr` directly. `stress_lsm()` allocates a 32-page buffer, lists active LSM module IDs, fetches self attributes for available `LSM_ATTR_*` constants, scans returned `struct lsm_ctx` entries, and records call-rate metrics.

Control flow: after mapping and synchronization, each iteration calls `lsm_list_modules()` with valid arguments and then invalid flags/NULL ids. It loops over attributes, calls `lsm_get_self_attr()`, classifies returned ids, then exercises invalid attr, invalid context pointer, invalid flags, and invalid negative `ctx_len` set behavior.

State and persistence: state is the temporary mmap buffer and booleans recording which ID categories were observed. No LSM configuration is intentionally changed; `set_self_attr` is used with invalid data as a negative test.

Dependencies/integration: gated by Linux syscall numbers and `linux/lsm.h`. Uses stress-ng mmap helpers, timing/metrics, proc-state sync, and debug logging.

Risks/test signals: syscall availability depends on kernel version and config; expected errno values are part of the test surface. Useful signals are skip on `ENOSYS`, failures on unexpected invalid-call behavior, rates for list/get calls, and debug output summarizing observed LSM ID classes.
