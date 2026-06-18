# sources/user-network-fs/samba/source4/torture/rpc/atsvc.c

## Purpose
`atsvc.c` is the RPC torture suite for the ATSVC scheduled-job interface. It enumerates jobs, fetches job information, adds a sample scheduled command, verifies it can be queried, and deletes it.

## Important APIs, types, and functions
The suite entry point is `torture_rpc_atsvc()`. Test helpers are `test_JobEnum()`, `test_JobAdd()`, `test_JobGetInfo()`, and `test_JobDel()`. It uses generated calls `dcerpc_atsvc_JobEnum_r()`, `dcerpc_atsvc_JobAdd_r()`, `dcerpc_atsvc_JobGetInfo_r()`, and `dcerpc_atsvc_JobDel_r()`, plus `struct atsvc_JobInfo`, `struct atsvc_enum_ctr`, and `ndr_table_atsvc`.

## Control flow
`test_JobEnum()` calls `JobEnum` with max buffer `0xffffffff`, resume handle zero, and an empty enum container, then iterates returned entries and calls `JobGetInfo` on each job ID. `test_JobAdd()` builds a periodic non-interactive Tuesday job for `foo.exe` at a fixed `job_time`, submits it with `JobAdd`, runs enumeration again, queries the returned job ID, and deletes exactly that ID with `JobDel`. The suite registers both `JobEnum` and `JobAdd` under an ATSVC RPC interface test case.

## State and persistence behavior
Enumeration is read-only, but `JobAdd` creates a scheduled job on the remote server and `JobDel` removes it. The persistent mutation is intended to be short-lived. If the test aborts between add and delete, a `foo.exe` job may remain on the target scheduler.

## Dependencies and integration points
The file depends on the generated ATSVC client stubs, DCE/RPC binding from the torture harness, server name resolution via `dcerpc_server_name()`, and scheduler service support on the target. It tests both transport-level NTSTATUS and ATSVC result status.

## Risks and edge cases
Adding scheduled jobs may require privileges and may be disabled or unsupported on modern targets. The hard-coded command and time are not intended to execute but still create real scheduler state. Cleanup is not protected by a `finally` style block if an assertion aborts after successful `JobAdd`. Existing jobs are queried during enum, so permission or corrupted job records can fail the read-only test.

## Test signals
Signals are successful ATSVC bind, OK transport and operation statuses for enum/add/get/delete, returned job IDs that can be queried, and no residual test job after deletion.
