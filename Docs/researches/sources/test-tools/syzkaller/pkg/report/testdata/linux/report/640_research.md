# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/640

## Purpose
This fixture validates a warning in `packet_release` from reference tracker free logic.

## Important APIs, types, and functions
Important frames include `ref_tracker_free`, `packet_release`, `__sock_release`, `sock_close`, `__fput`, `task_work_run`, `do_exit`, `do_group_exit`, and `__x64_sys_exit_group`.

## Control flow
Process exit closes a packet socket, file release runs socket release, and packet socket cleanup warns in ref-tracker code.

## State and persistence behavior
The fixture persists task-exit context, socket release stack, and warning metadata. It does not include panic metadata.

## Dependencies and integration points
It integrates AF_PACKET socket teardown with Linux warning parsing and ref-tracker diagnostics.

## Risks and test signals
The parser should title the report `WARNING in packet_release`, not `ref_tracker_free`.
