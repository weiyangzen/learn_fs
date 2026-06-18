# sources/storage-engines/rocksdb/tools/pflag

## Purpose
`pflag` is a Bash process monitor. It periodically samples one resource metric for a target PID and takes an action when the measured value breaches a threshold. Supported metrics are virtual memory, RSS, and CPU time on Linux.

## Important APIs, Types, and Functions
The script defines `oscheck`, `verbose`, `warn`, `die`, `dump_config`, `usage`, `set_defaults_if_noopt_given`, and `validate_options`. Runtime variables include `PID`, `VAR`, `LIMIT`, `WAIT`, `N`, `ACTION`, and `DEBUG`. It uses `/bin/ps h -p "$PID" -o "$VAR"` and a Perl expression to normalize `m`/`g` suffixes.

## Control Flow
After parsing options with `getopts`, the script checks OS support, applies defaults (`VAR=vsz`, `LIMIT=1024000`, `WAIT=5`, high `N`, `ACTION=warn`), optionally dumps configuration, then loops until the process exits or the metric breaches the threshold. On breach it either warns and continues, kills the process, or exits after printing process details.

## State and Persistence
No persistent state is written. The only durable side effect can be process termination when `ACTION=kill`. Output goes to stdout/stderr.

## Dependencies and Integration Points
It depends on Bash, Linux `ps`, Perl, `kill`, `date`, and host process accounting. It is suitable for wrapping long-running benchmarks such as `db_bench`, although no direct caller is in this subset.

## Risks
The `-w` option is documented but the `getopts` string uses `t` instead of `w`, so wait parsing appears broken. `N` is logged but not decremented in the loop, so cycle limiting is ineffective. Numeric comparisons assume normalized integer values and can fail for unexpected `ps` output. `exit -1` maps to shell status 255. The script is Linux-only.

## Test Signals
No dedicated tests are present in this subset. Useful validation would include short-lived PID monitoring, threshold breach for each action, unit checks for `-w` parsing, and CPU-time threshold parsing.
