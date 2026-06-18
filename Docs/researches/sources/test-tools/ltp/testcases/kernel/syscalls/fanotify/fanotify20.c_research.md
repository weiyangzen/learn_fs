# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify20.c

Purpose: validates `FAN_REPORT_PIDFD` initialization rules. It checks that combining pidfd reporting with `FAN_REPORT_TID` fails with `EINVAL`, while combining pidfd reporting with fid/dfid-name reporting remains valid.

Important APIs/types/functions: `fanotify_init`, `FAN_REPORT_PIDFD`, `FAN_REPORT_TID`, `FAN_REPORT_FID`, `FAN_REPORT_DFID_NAME`, `REQUIRE_FANOTIFY_INIT_FLAGS_SUPPORTED_ON_FS`, and `TST_EXP_FD_OR_FAIL`.

Control flow: `do_setup()` verifies `FAN_REPORT_PIDFD` support on the mounted test path. `do_test()` runs the two table cases, calling `fanotify_init` with the specified flags and asserting either the expected `EINVAL` or a valid fd that is then closed.

State/persistence behavior: no filesystem events are generated. State is limited to feature probing and the transient fanotify group fd.

Dependencies/integration: needs root and LTP's all-filesystems mount harness. It depends on Linux pidfd fanotify support introduced in v5.15-rc1 and gracefully skips if unsupported.

Risks/test signals: narrow API contract test. Passing is either the precise expected errno for invalid flag combinations or successful fd creation for compatible reporting flags; any other init failure is a regression or unsupported environment.
