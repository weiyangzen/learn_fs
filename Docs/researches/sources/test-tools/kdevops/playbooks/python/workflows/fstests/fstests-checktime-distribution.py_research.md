# sources/test-tools/kdevops/playbooks/python/workflows/fstests/fstests-checktime-distribution.py

Purpose: Converts fstests `check.time` files into `.distribution` CSV files showing runtime buckets, counts, and percentages.

Key APIs and flow: `main()` walks a results directory, finds files ending in `check.time`, removes any existing `.distribution`, parses lines matching `group/number time`, counts tests per integer time value, sorts by runtime with `OrderedDict`, and writes `time,count,percentage` rows.

State, dependencies, integration: Persists one sibling `<check.time>.distribution` file per input. Uses Python stdlib only; constants for `sort-expunges.sh` are present but unused. It integrates with fstests runtime analysis.

Risks and test signals: Division by zero occurs for empty or wholly unparsable files; files are opened without context managers; non-word group names are ignored by regex; unused variables suggest drift. Tests should cover normal check.time, empty input, malformed lines, repeated runtimes, and pre-existing distribution replacement.
