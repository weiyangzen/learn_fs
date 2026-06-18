
# sources/user-network-fs/samba/source4/torture/masktest.c

## Purpose
`masktest.c` is a standalone SMB wildcard matching torture program. It creates test files on a target share, lists them through the server using SMB directory search calls, computes Samba's local `ms_fnmatch_protocol()` expectation for the same mask/file pair, and reports mismatches. It is aimed at detecting protocol-dialect differences and server behavior drift around DOS/SMB wildcard semantics, including long/short name interactions and special dot entries.

## Important APIs, Types, And Functions
Key globals configure fuzzing and reporting: `showall`, `old_list`, `maskchars`, `filechars`, `die_on_error`, `NumLoops`, and `max_length`. `struct masktest_state` carries a `TALLOC_CTX` into list callbacks. `reg_match_one()` wraps `ms_fnmatch_protocol()` and adds SMB-specific special cases for `*.*`, `.`, and `..`. `reg_test()` computes the three-character expected result for dot, dotdot, and the test file. `connect_one()` parses a UNC share and calls `smbcli_full_connection()`. `listfn()` is the `smbcli_list_new()` callback that records which class of entry the server returned and saves long/short names. `get_real_name()` obtains the server-side long and 8.3 short names by listing the `\\masktest` directory. `testpair()` creates one file, lists by mask, compares server and local results, prints mismatches, and unlinks the file. `test_mask()` either consumes explicit mask/file argument pairs or generates random masks and filenames indefinitely or until `NumLoops`.

## Control Flow
`main()` initializes talloc, Samba command-line handling, popt options, loadparm, logging, events, GENSEC, SMB client options, and the server connection. It normalizes the UNC path from `/` to `\\`, connects as workstation `masktest`, seeds the random generator after connection setup, and invokes `test_mask()`. `test_mask()` creates `\\masktest`, clears old entries, then either runs supplied pairs or a random fuzz loop. Each `testpair()` creates the file, queries the real server names, performs a masked listing, computes the local expectation, prints when results differ or `--showall` is set, and cleans up the file. The directory is removed at the end.

## State And Persistence
Runtime state is mostly global and process-local. `resultp` points at the current three-character result buffer used by `listfn()`, and `last_hit`/`f_info_hit` retain the most recent directory-listing match. Persistent remote state is limited to a temporary `\\masktest` directory and files under it; cleanup attempts are explicit but may leave artifacts if the process exits during a failure or `--dieonerror`. The random seed is printed so fuzz failures can be reproduced.

## Dependencies
The file depends on Samba client libraries (`libcli/libcli.h`), command-line and credentials helpers, talloc, tevent, loadparm, resolver, GENSEC, file/dir system wrappers, and protocol-aware name matching via `ms_fnmatch_protocol()`. It depends on SMB server support for open, close, list, unlink, wildcard unlink, mkdir, and rmdir operations.

## Integration Points
This program is an external torture utility rather than a registered `smbtorture` suite in this file. It integrates with Samba credentials and connection options through `POPT_COMMON_*` tables and `samba_cmdline_get_creds()`. Results validate both server behavior and Samba's internal wildcard matching rules for the negotiated protocol dialect.

## Risks
The code uses several globals, so concurrent use within one process would be unsafe. `get_real_name()` assumes `short_name` is initialized and dereferenceable after listing; severe list failure could leave `long_name` unset. Random generation avoids dot-only filenames and dotdot masks, but it can still generate large search spaces or server-expensive masks. Cleanup is best-effort and remote artifacts can remain after aborts. The `old_list` compatibility special case changes expected `*.*` semantics and must be used deliberately.

## Test Signals
Strong signals are reproducible mismatch lines showing `server_result expected_result count mask file real_names`, absence of mismatches across many seeded loops, successful cleanup of `\\masktest`, and coverage across protocol dialects. Useful focused tests include explicit pairs around `.`, `..`, `*`, `?`, `*.*`, short-name aliases, and protocol versions at or below `LANMAN1`.
