# sources/user-network-fs/libfuse/util/parse-backtrace.sh

## Purpose
Developer helper script that parses glibc `backtrace_symbols`-style traces and resolves addresses/symbol offsets with `addr2line`.

## Important APIs, Types, And Functions
- Options: `-t '<trace>'`, `-p`/`-f <program path>`, `-h`.
- `parse_glibc_trace` extracts filenames and symbols, resolves relative binary names through `PROGRAM_PATH` or `which`, and invokes `addr2line -a -p -s -C -f -i`.

## Control Flow
The script creates a temp file, parses options, requires a trace, then iterates trace lines containing brackets. It strips non-breaking spaces, trims syslog prefixes, extracts the binary and symbol between parentheses, resolves the binary path, and prints addr2line output.

## State And Persistence
Creates and removes a temporary file named `backtrace.XXX` in the current directory. No other persistent state.

## Dependencies And Integration Points
Depends on Bash, `mktemp`, `sed`, `egrep`, `awk`, `which`, and `addr2line`. Intended for troubleshooting libfuse crashes.

## Risks
Several variables are unquoted in command invocations, so paths with spaces or shell metacharacters can misbehave. The line `echo $line line | sed -e 's/.*://'` appears to include an unintended literal `line`. Only glibc trace format is supported.

## Test Signals
Test absolute and PATH-relative binaries, paths with spaces, traces copied from syslog, missing `-t`, unsupported trace formats, and symbols that are raw offsets.
