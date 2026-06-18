# sources/user-network-fs/samba/source3/torture/test_rpc_samr.c

## Purpose
This is a focused cmocka regression test for SAMR password-complexity command expansion, specifically `check_password_complexity_internal()`. It validates how a configured command string containing `%u` is expanded for a candidate username, including shell quoting, dangerous characters, option-looking names, Unicode input, fallback substitution, and invalid principal-name rejection. Many cases are explicitly tied to hardening around command injection, including the fallback marker `__CVE-2026-4408_FallbackUsername__`.

## Important APIs, Types, And Functions
`struct cmd_expansion` defines each test vector: `lp_cmd`, `username`, expected `result_cmd`, and expected `NTSTATUS`. The `expansions[]` table is the main test specification. `setup_talloc_context()` and `teardown_talloc_context()` provide a per-suite talloc root through cmocka state. `test_expansions()` iterates the vector table and calls `check_password_complexity_internal(mem_ctx, t.lp_cmd, t.username, &result_cmd)`.

The code uses `NT_STATUS_IS_OK()`, `NT_STATUS_EQUAL()`, and `nt_errstr()` for status handling, `assert_int_equal()` for cmocka assertions, and conditional `debug_message()` output. `main()` registers the single unit test and switches to Subunit output when stdout is not a terminal.

## Control Flow
The cmocka runner creates a talloc context, runs `test_expansions()`, and frees the context. For each table row, the test invokes the SAMR utility under test. If both expected and actual statuses are success, the generated command must exactly match `result_cmd`. If the actual status equals the expected failure status, the case passes without comparing command output. Any status mismatch or command mismatch fails the test immediately through cmocka assertions.

## State And Persistence Behavior
The test has no persistent runtime state. All allocations are under the cmocka-provided talloc context and are freed by `teardown_talloc_context()`. The only external state is stdout/stderr-style test reporting. The command strings are not executed; the test validates expansion output only.

## Dependencies And Integration Points
The file includes generated SAMR NDR headers and `rpc_server/samr/srv_samr_util.h`, which exposes the internal password-complexity helper. It depends on cmocka, talloc, and Samba NTSTATUS utilities. It integrates as a standalone unit-test executable with its own `main()`, unlike many smbtorture tests that export `run_*` entry points.

## Risks And Edge Cases
The table is security-sensitive because it encodes expected sanitization behavior for metacharacters such as quotes, backslashes, redirection, command substitution, wildcard characters, leading dashes, spaces, percent expansion, and non-ASCII usernames. A legitimate change in quoting policy must update many exact expected strings. `SAMR_DEBUG_VERBOSE` is set to true, so verbose messages are enabled by default; non-tty output is mitigated by Subunit mode but local terminal output can be noisy. The test validates command construction, not shell execution behavior, so shell-specific semantics remain outside its coverage.

## Test Signals
Passing means every command expansion either matches the exact expected command string or returns the exact expected NTSTATUS. Failures print the vector index, input command, username, actual status, expected status, and mismatched command strings, which gives direct repair signals for the sanitization logic.
