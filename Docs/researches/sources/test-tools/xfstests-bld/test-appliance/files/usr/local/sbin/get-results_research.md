# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/get-results

Purpose: extracts summary or failure lines from a result log.

Important flow: choose default summary regex or `--failures/-F` regex, read input files or stdin, grep selected lines, and in failure mode detect unmatched `BEGIN` without `END` to report a missing END for the last started test.

State and dependencies: no persistent state; depends on grep, shell, and xfstests log marker conventions.

Integration points: useful for local result inspection and overlaps with shutdown summary extraction.

Risks and test signals: regexes are shell variables and must track log formats. Failure mode reads the input multiple times, so stdin is not suitable there unless buffered externally. Tests should cover file input and interrupted test logs.
