# sources/user-network-fs/samba/source4/torture/ndr/atsvc.c

## Purpose

This file defines a compact Samba NDR torture suite for ATSVC RPC marshalling. It verifies that generated NDR pull code for selected AT Scheduler service operations decodes known wire byte streams into the expected generated C structures. The coverage is fixture-oriented rather than live RPC-oriented: each test feeds static byte arrays into the NDR torture helpers and asserts decoded fields.

## Important APIs, Types, and Functions

- `ndr_atsvc_suite()` creates the `atsvc` NDR torture suite and registers pull tests with `torture_suite_add_ndr_pull_fn_test()`.
- Generated RPC/NDR types under test are `struct atsvc_JobEnum`, `struct atsvc_JobAdd`, `struct atsvc_JobDel`, and `struct atsvc_JobGetInfo` from `librpc/gen_ndr/ndr_atsvc.h`.
- Static fixture arrays encode in/out stubs: `jobenum_in_data`, `jobenum_out_data`, `jobadd_in_data`, `jobadd_out_data`, `jobdel_in_data`, `jobdel_out_data`, `jobgetinfo_in_data`, and `jobgetinfo_out_data`.
- Check callbacks `jobenum_in_check()`, `jobenum_out_check()`, `jobadd_in_check()`, `jobadd_out_check()`, `jobdel_in_check()`, `jobdel_out_check()`, `jobgetinfo_in_check()`, and `jobgetinfo_out_check()` validate the decoded structures with torture assertions.

## Control Flow

Suite construction is linear. `ndr_atsvc_suite()` allocates a suite named `atsvc` and adds eight NDR pull tests. Each registration specifies the operation type, fixture byte array, NDR direction (`NDR_IN` or `NDR_OUT`), and a callback that validates decoded output.

The JobEnum input fixture decodes a server name pointer/string for `WIN2KDC1`, an empty job enumeration container, preferred max length of `-1`, and a resume handle of zero. The JobEnum output fixture decodes seven entries, checks the first job's ID, time, day flags, command string `foo.exe`, total entry count, resume handle, and NT success result.

The JobAdd input fixture checks a server name and job information including time `84600000`, day-of-week bit `0x2`, flags `17`, and command `foo.exe`; its output fixture checks returned job ID `14` and success. JobDel input checks deletion range `14..14`; its output fixture intentionally does not assert the return value beyond a FIXME noting an unknown `0x00000ede` status. JobGetInfo input checks server name and job ID `1`; output checks a non-null job info pointer and the expected time, calendar flags, flags `0x13`, and command.

## State and Persistence Behavior

There is no persistent state and no live scheduler interaction. All state is local, static test data plus decoded temporary structures allocated by the NDR torture framework. The tests are deterministic so long as the generated ATSVC NDR definitions and scalar/string decoding semantics remain compatible with the fixture data.

## Dependencies and Integration Points

The file depends on Samba's NDR torture harness (`torture/ndr/ndr.h`), generated ATSVC NDR declarations (`librpc/gen_ndr/ndr_atsvc.h`), and suite prototype integration (`torture/ndr/proto.h`). It integrates into the broader NDR test registry through the exported `ndr_atsvc_suite()` function. The generated pull functions are selected by the `torture_suite_add_ndr_pull_fn_test()` macro/function based on the operation type name supplied in each registration.

## Risks and Edge Cases

- The byte arrays encode exact historical wire layouts. Changes to generated IDL, pointer layout, conformant/varying string handling, status typing, or structure defaults can break tests even if higher-level ATSVC behavior still works.
- Only selected fields are asserted. For JobEnum output, only the first of seven entries is deeply checked, so regressions in later entries could be missed.
- `jobdel_out_check()` accepts the fixture without validating the unknown return code, leaving a known gap in status semantics coverage.
- Pointer assumptions are explicit for fields such as `servername`, `ctr`, `first_entry`, `resume_handle`, `job_id`, and `job_info`; if generated code changes pointer ownership or nullability, these tests will catch some but not all consequences.

## Test Signals

Passing this suite means the ATSVC generated NDR pull path can decode the embedded fixtures and populate key fields for JobEnum, JobAdd, JobDel, and JobGetInfo in both input and output directions. Failures usually indicate an IDL/NDR layout regression, endian/alignment issue, string decoding change, pointer conformance issue, or a changed interpretation of ATSVC status/result fields. The strongest positive signals are the decoded Unicode server/command strings, job time and flag values, total/resume counters, returned job ID, and NT success statuses for the checked operations.
