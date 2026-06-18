# sources/user-network-fs/samba/source4/torture/rpc/torture_rpc.h

## Purpose

`torture_rpc.h` is the shared public header for Samba source4 RPC torture suites. It defines the RPC testcase wrapper types and declares helpers for opening RPC connections, creating domain joins, adding RPC tests to suites, and initializing authenticated, anonymous, or machine-account testcases.

## Important APIs, Types, and Functions

`struct torture_rpc_tcase` embeds `struct torture_tcase` and adds the target NDR interface table, optional machine name, and optional setup/teardown callbacks that receive the DCE/RPC pipe. `struct torture_rpc_tcase_data` carries the joined account context, pipe, and credentials used by testcase setup. Connection declarations are `torture_rpc_connection()` and `torture_rpc_connection_with_binding()`. Domain helpers include `torture_join_domain()`, `torture_join_sid()`, and `torture_leave_domain()`. Suite builders include `torture_suite_add_rpc_iface_tcase()`, `torture_suite_add_rpc_setup_tcase()`, anonymous and machine variants, plus test registration helpers for plain pipe tests, join-aware tests, setup-data tests, arbitrary userdata tests, and credential-aware tests.

## Control Flow

The header has no runtime control flow. At compile time, individual RPC torture files include it to register tests against generated NDR interface tables. At runtime, implementations behind these declarations open DCE/RPC pipes before test functions run and invoke optional setup/teardown wrappers around each testcase.

## State and Persistence Behavior

The declared API can create persistent remote state indirectly through domain join helpers and machine-account testcases. The header's data structs hold per-testcase pipe and credential state, but ownership and cleanup are implemented elsewhere. The machine testcase helpers imply lifecycle management of temporary trust accounts.

## Dependencies and Integration Points

It includes the core torture framework, credentials, DRSUAPI torture declarations, libnet join types, DCE/RPC binding types, raw CLI types, spoolss NDR types, and generated `torture/rpc/proto.h`. It is the integration contract between suite source files and common RPC torture infrastructure.

## Risks and Edge Cases

Because this header is a broad coupling point, signature drift affects many suites. Function pointer signatures are strict; mismatching a test helper with the wrong registration function can compile with casts in some callers but fail at runtime. The header exposes only forward-declared join state for some helpers, so consumers rely on accessor functions and must not assume layout.

## Test Signals

Compile success across RPC torture suites is the main signal for this header. Runtime signals come from suites successfully creating authenticated, anonymous, BDC, workstation, setup-data, and credential-aware testcases through the declared helpers.
