# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/common.h

Purpose: shared declarations and small macros for libnetapi tests. It lets separate test modules share the common popt option table, test-suite entry point declarations, status-print helpers, and portable array/zeroing macros.

Important APIs/types: declares `popt_common_callback`, `popt_common_netapi_examples`, `test_netuseradd`, and module functions `netapitest_localgroup`, `netapitest_user`, `netapitest_group`, `netapitest_display`, `netapitest_share`, `netapitest_file`, `netapitest_server`, and `netapitest_wksta`. Defines `POPT_COMMON_LIBNETAPI_EXAMPLES`, fallback `POPT_TABLEEND`, fallback `ARRAY_SIZE`, `NETAPI_STATUS`, `NETAPI_STATUS_MSG`, and `ZERO_STRUCT`.

Control flow: no executable code is present. Macro expansion controls how test programs include common popt options and how failures are reported with source line numbers and `libnetapi_get_error_string`.

State and persistence: no state is stored. Macros operate on caller variables and print diagnostics to stdout/stderr through the call sites.

Dependencies/integration: includes popt declarations and assumes `NET_API_STATUS`, `struct libnetapi_ctx`, and `libnetapi_get_error_string` are visible from the including translation unit's `<netapi.h>`. It ties the individual test modules into `netapitest.c`.

Risks: `ZERO_STRUCT` uses `memset`, so including files must include `<string.h>`. The status macros evaluate status and context expressions directly and print numeric status as signed `%d`, which can be misleading for large unsigned `NET_API_STATUS` values. The shared fixed test function names mean adding modules requires header and build updates.

Test signals: build coverage is the main signal. Compile all test translation units with this header and verify failure messages include line numbers and readable libnetapi error strings.
