# sources/security-integrity/selinux/libsepol/cil/src/cil_log.c

## Purpose
`cil_log.c` implements the CIL logging shim. It provides a configurable callback and log level used by parser, verification, allocation wrappers, and other CIL subsystems.

## Important APIs, Types, And Functions
Public functions are `cil_set_log_handler`, `cil_vlog`, `cil_log`, `cil_set_log_level`, and `cil_get_log_level`. The default handler writes messages to `stderr`. Messages are formatted into a fixed `MAX_LOG_SIZE` buffer.

## Control Flow
`cil_log` wraps varargs and delegates to `cil_vlog`. `cil_vlog` emits a message only when the current global log level is greater than or equal to the message level. If `vsnprintf` reports truncation, it emits a truncation marker.

## State And Persistence Behavior
The file owns two process-global variables: current log level and current handler function pointer. It persists no data except through the caller-provided handler side effects.

## Dependencies And Integration Points
It includes public `cil/cil.h` for log level enum definitions. All CIL error reporting routes through this module either directly or indirectly.

## Risks And Edge Cases
Global handler and level are not synchronized, so concurrent users could race. The callback receives `cil_log_level` rather than the original message level, which is a behavioral detail consumers may rely on or trip over. Long messages are truncated to 512 bytes plus marker.

## Test Signals
Tests should set custom handlers, vary log levels, check suppression/emission, and verify truncation behavior. Integration tests should assert diagnostics for parse and verification failures.
