# sources/sync-backup/bup/wvtest-bash.sh

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/wvtest-bash.sh -->
## sources/sync-backup/bup/wvtest-bash.sh

Purpose: this Bash-specific extension augments the portable `wvtest.sh` assertions with stack tracking, caller location discovery, SIGPIPE-aware pipeline assertions, and regex matching. It is sourced only when `BASH_VERSION` is set, allowing the base harness to stay compatible with `/bin/sh`.

Important APIs and functions: `_wvbtstack` records asserted command text. `_wvpushcall` and `_wvpopcall` maintain that stack. `_wvbacktrace` walks Bash `FUNCNAME`, `BASH_SOURCE`, and `BASH_LINENO` to print nested WV assertion calls. `_wvfind_caller` records `WVCALLER_FILE` and `WVCALLER_LINE`. `WVPIPE` runs a command like `WVPASS` but treats SIGPIPE as success, using a runtime-computed `_wvsigpipe_rc`. `wv-match-rx` checks a string against a Bash regex and emits diagnostic context.

Control flow: on source, the script initializes the stack and computes the platform SIGPIPE exit code via `dev/python`. Assertion helpers push call text before running commands, find the caller, and pop on success. Failures delegate to `_wvcheck` from `wvtest.sh`, which exits the test script. `wv-match-rx` prints both compared values before the regex test.

State and persistence: all state is process-local shell state: `_wvbtstack`, `_wvsigpipe_rc`, `WVCALLER_FILE`, and `WVCALLER_LINE`. It does not persist files. It depends on stderr output as the test reporting channel.

Dependencies and integration points: it requires Bash arrays, Bash regex syntax, Bash stack variables, `sed`, and `dev/python`. It is loaded by `wvtest.sh`, so its functions are part of the wider Bup shell test framework.

Risks: failures in `dev/python` abort sourcing. Bash-specific syntax must never be parsed by plain `sh`, which is why the base harness gates sourcing. `wv-match-rx` prints failure text but does not explicitly exit; callers need the surrounding harness to interpret output. SIGPIPE handling assumes conventional shell exit status `128 + signal`.

Test signals: tests using nested `WVPASS` or `WVFAIL` should show meaningful backtraces. Pipeline tests such as producer piped into `head` should pass via `WVPIPE` when the producer receives SIGPIPE. Regex tests should emit clear "Matching" and "Against" diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/wvtest-bash.sh -->
