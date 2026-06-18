# File Research: sources/local-fs/xfsdump/common/exit.h

## Summary
Defines process exit codes and a small string conversion helper for xfsdump/xfsrestore main and child processes.

## Main Contents
- `EXIT_NORMAL` = `0`, for successful completion or “do not exit”.
- `EXIT_ERROR` = `1`, for resource errors or exhaustion.
- `EXIT_INTERRUPT` = `2`, for operator or device interruptions.
- `EXIT_FAULT` = `4`, for internal code faults.
- `exit_codestring()` maps those constants to stable labels.

## Risks
The constants are public process status semantics. Scripts and supervisor code may depend on these exact values.

`EXIT_NORMAL` is documented as both normal completion and “don’t exit”, so callers must preserve contextual meaning.
