# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netapitest.c

Purpose: main executable entry point for the libnetapi integration test suite. It initializes libnetapi, parses common options plus a required hostname, and runs the module tests in a fixed sequence.

Important APIs/functions: `main` calls `libnetapi_init`, configures popt with `POPT_COMMON_LIBNETAPI_EXAMPLES`, retrieves `hostname`, then invokes `netapitest_localgroup`, `netapitest_user`, `netapitest_group`, `netapitest_display`, `netapitest_share`, `netapitest_file`, `netapitest_server`, and `netapitest_wksta`.

Control flow: test execution is fail-fast. If a module returns nonzero, the remaining modules are skipped, a suite failure message is printed, and cleanup runs. Missing hostname prints popt help and exits through the common cleanup path.

State and persistence: creates a process-local `libnetapi_ctx` and frees it before exit. The modules it calls may persistently create/delete users, groups, local groups, and shares on the target host. This driver itself persists nothing.

Dependencies/integration: depends on popt, public `netapi.h`, and the declarations in `common.h`. The build file links this driver with all module sources into the `netapitest` binary.

Risks: because modules are destructive and fail-fast, a failure can leave target-side objects until each module's own cleanup runs. The ordering puts localgroup before user/group/share tests; later modules may depend on privileges established through the parsed credentials. If `libnetapi_init` fails, popt is never initialized and the status is returned directly.

Test signals: run against an isolated Samba test instance with admin credentials. Verify missing-hostname behavior, credential option parsing, fail-fast semantics, cleanup after failures, and final process exit code.
