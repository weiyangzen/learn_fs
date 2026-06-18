# sources/user-network-fs/samba/source4/torture/rpc/rpc.c

## Purpose
This file is the central DCE/RPC torture harness and registry for Samba's `rpc` suite. It turns the user-supplied `binding` torture setting into connected `dcerpc_pipe` objects, provides standard RPC test-case setup/teardown variants, wraps RPC test callbacks into the generic torture framework, supports temporary workstation and BDC domain joins for machine-account tests, and registers all RPC sub-suites and simple tests.

## Important APIs, types, and functions
`torture_rpc_binding()` parses the `binding` setting into a `dcerpc_binding`. `torture_rpc_connection()` and `torture_rpc_connection_with_binding()` initialize DCE/RPC support and connect to a generated NDR interface with command-line credentials. `torture_rpc_connection_transport()` adjusts transport, association group, and extra binding flags before connecting.

Setup helpers include `torture_rpc_setup()`, `torture_rpc_setup_anonymous()`, `torture_rpc_setup_machine_workstation()`, and `torture_rpc_setup_machine_bdc()`. They populate `struct torture_rpc_tcase_data` with credentials, joined machine context where needed, and a connected pipe. `torture_rpc_teardown()` leaves any joined domain and frees case data.

Test registration helpers include `torture_suite_init_rpc_tcase()`, `torture_suite_add_rpc_iface_tcase()`, `torture_suite_add_anon_rpc_iface_tcase()`, `torture_suite_add_machine_workstation_rpc_iface_tcase()`, `torture_suite_add_machine_bdc_rpc_iface_tcase()`, `torture_rpc_tcase_add_test()`, `torture_rpc_tcase_add_test_creds()`, `torture_rpc_tcase_add_test_join()`, `torture_rpc_tcase_add_test_ex()`, `torture_rpc_tcase_add_test_setup()`, and `torture_suite_add_rpc_setup_tcase()`.

## Control flow
Generic RPC cases start by parsing the binding string, connecting to the target NDR table with `samba_cmdline_get_creds()`, and storing the pipe in case data. Anonymous cases use `cli_credentials_init_anon()`. Machine-account cases call `torture_join_domain()` with `ACB_WSTRUST` or `ACB_SVRTRUST`, update the credential pointer with joined machine credentials, then connect using those credentials. Teardown reverses joined-machine setup through `torture_leave_domain()`.

Each `torture_rpc_tcase_add_*` function allocates a `struct torture_test`, records the real callback in `test->fn`, selects an adapter such as `torture_rpc_wrap_test_creds()`, and appends it to the case list with `DLIST_ADD_END()`. The adapters recover the active `torture_rpc_tcase_data`, then call the typed callback with the pipe plus optional credentials, join context, userdata, or per-test setup/teardown data.

`torture_rpc_init()` creates the top-level `rpc` suite, calls `ndr_table_init()`, adds many simple and nested tests for LSA, SAMR, Netlogon, PAC, SRVSVC, SPOOLSS, WINREG, DRSUAPI, SMB/RPC bind edge cases, and other interfaces, sets the suite description, and registers it with `torture_register_suite()`.

## State and persistence
The harness maintains per-test-case state only for the duration of the case: connected pipe, credential pointer, and optional `test_join` context. It mutates the target domain when machine-account cases join temporary workstation or BDC accounts, and teardown is responsible for cleanup. The local process stores no durable data. The `binding` torture setting is mandatory for most RPC tests.

## Dependencies and integration points
This file is the integration point between the generic torture framework, Samba command-line credentials, DCE/RPC binding/pipe APIs, NDR interface tables, and domain-join helpers. It exposes public helper functions used by many files in `source4/torture/rpc/`, including `remote_pac.c` and the Samba3 suite. It depends on `torture/rpc/torture_rpc.h` for shared structs and prototypes and on generated NDR table symbols for each registered RPC interface.

## Risks
Because this file centralizes setup, connection, and wrapper behavior, changes can affect many RPC torture tests at once. Failure to parse the binding setting cleanly prevents broad suite execution. Machine-account setup uses real domain joins, so missing teardown can leave temporary accounts. The wrapper functions rely on callback signatures matching the selected add helper; a mismatched cast compiles through `void *` storage patterns but fails at runtime. `torture_rpc_wrap_test_setup()` does not call its teardown callback if the test function itself fails, so custom setup tests must be careful about externally persistent state.

## Test signals
Primary signals are successful binding parsing, `dcerpc_pipe_connect_b()` success, correct test callback invocation, and clean teardown of joined machine accounts. At suite level, the signal is that `torture_rpc_init()` registers `rpc` and includes expected nested suites such as `netlogon`, `remote_pac`, `samba3`, DRSUAPI, SRVSVC, SPOOLSS, WINREG, and bind/auth tests.
