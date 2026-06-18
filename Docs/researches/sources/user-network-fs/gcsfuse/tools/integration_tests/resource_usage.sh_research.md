# sources/user-network-fs/gcsfuse/tools/integration_tests/resource_usage.sh

## Purpose

`resource_usage.sh` collects and prints coarse CPU, memory, and disk usage during long integration test runs. It supports a collection mode that writes samples to a file and a print mode that renders text graphs from that file.

## Important APIs, Types, and Functions

The script uses `set -euo pipefail`, constants for 10-second interval and 3-hour duration, and commands `COLLECT` and `PRINT`. `usage` prints help. `get_cpu_usage` parses `top`, `get_mem_usage` parses `free`, and `get_disk_usage` parses `df -P /`. `collect_all_metric` writes a header and sample rows. `print_each_metric` reads columns into an associative array and prints vertical ASCII graphs. A trap exits cleanly on SIGINT/SIGTERM.

## Control Flow

The script validates exactly two arguments, records command and file path, installs the signal trap, and dispatches to collect or print. Collection loops until Bash `SECONDS` reaches the duration, appending `CPU MEM DISK` samples. Print reads the file header, groups values by metric, computes a capped graph ceiling, and prints one graph per resource.

## State and Persistence Behavior

Collection overwrites the target file header and appends samples. Print mode reads the target file but does not modify it. The script depends on process runtime through `SECONDS` and host system commands.

## Dependencies and Integration Points

It depends on Bash, `top`, `free`, `df`, `awk`, `tail`, and basic shell builtins. It is intended for Kokoro/VM integration runs with a 3-hour timeout.

## Risks and Edge Cases

Parsing `top` is locale/platform dependent; the script expects `%Cpu` and idle in field 8. `print_each_metric` assumes well-formed rows with all columns. Under `set -u`, missing associative array entries or empty files can fail. Disk usage is only root filesystem usage, not necessarily cache or mount-specific usage.

## Test Signals

Useful signals are a file beginning with `CPU MEM DISK`, sample rows every 10 seconds, and printable graphs for each metric. Failures indicate missing host utilities, format drift, or malformed sample files.
