# sources/user-network-fs/samba/source4/torture/rap/rap.c

Purpose: This is the main RAP torture registration file and the home of basic Remote Administration Protocol tests for shares, servers, sessions, remote time-of-day, and raw call scanning.

Important APIs, types, and functions: Basic tests use `rap_NetShareEnum`, `rap_NetServerEnum2`, `rap_WserverGetInfo`, `rap_NetSessionEnum`, `rap_NetSessionGetInfo`, and `rap_NetRemoteTOD`. `torture_rap_scan()` probes call numbers with `new_rap_cli_call()` and `rap_cli_do_call()`. `torture_rap_init()` builds the root `rap` suite and attaches RPC, printing, and SAM sub-suites.

Control flow: Share and server enum tests issue one RAP call and print returned records. Server getinfo checks levels 0 and 1 with success statuses. Session enum queries level 2 and asserts non-empty computer and user names for each record. Session getinfo first enumerates sessions, normalizes each session name to a UNC form if needed, and queries level 2. Remote TOD performs a single success check. The scanner iterates call numbers `0..0xfffe` and reports calls that return `NT_STATUS_INVALID_PARAMETER`, indicating probable RAP handlers.

State and persistence behavior: Basic tests are mostly read-only. They allocate transient RAP request/response structures and print information. `torture_rap_scan()` is exploratory and noisy but does not persist state.

Dependencies and integration points: It depends on `libcli/rap/rap.h`, SMB tree state, torture settings, and sub-suite constructors `torture_rap_rpc()`, `torture_rap_printing()`, and `torture_rap_sam()`. `torture_rap_init()` is the entry point registered with the Samba torture harness.

Risks: The tests assume RAP support and enough server state to return sessions. The server enum test assigns `servertype` twice, leaving only `0x80000000`, which is intentional or legacy but can surprise readers. The scan test is broad and may be slow or noisy.

Test signals: Success indicates basic RAP request marshalling, status handling, share/server/session enumeration, session detail lookup, and remote time query behavior remain functional.
