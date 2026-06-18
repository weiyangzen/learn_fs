# sources/test-tools/kdevops/scripts/workflows/generic/crash_report.py

## Purpose
Builds a text summary of collected crash, corruption, and warning logs under the `crashes/` directory.

## Important APIs
`clean_lines(text)` strips ANSI escapes and non-printable characters. `collect_host_logs(host_path)` prefers decoded crash variants over raw crash files, includes warnings and corruption files, and returns typed entries. `generate_commit_log()` prints a Markdown-like report grouped by host.

## Control flow
When run, the script exits 0 with a no-crashes message if `crashes/` does not exist. Otherwise it iterates host directories, collects logs, and prints fenced cleaned content for each entry.

## State and dependencies
Read-only over crash output files. Uses Python `pathlib`, `re`, and `os`.

## Integration points
Consumes files produced by `KernelCrashWatchdog`, suitable for commit messages, CI logs, or failure summaries.

## Risks and test signals
Typo in the no-crashes message says "isues". Report size can grow large because full log contents are printed. Test with decoded and raw duplicate crash files to confirm decoded preference.
