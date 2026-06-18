## sources/security-integrity/attr/test/run

Purpose: Perl transcript test runner.

It reads test files with `$` commands plus `<` stdin and `>` expected output lines, substitutes environment variables, runs each command in a per-test temp directory, captures combined stdout/stderr, supports regex expected lines with `~`, and implements built-ins like `cd`, `umask`, `su`, `sg`, `require_root`, `export`, and `unset`. State includes temp directories, environment changes, effective uid/gid changes, and pass/fail counters. Dependencies are Perl, POSIX privilege APIs, fork/pipe/exec, and shell fallback for metacharacters. Risks include taint disabled, combined stderr/stdout hiding stream differences, privilege mutation complexity, and shell quoting in fallback mode. Test signal is the runner’s command count and failed count.
