# File Research: sources/os/bsd/netbsd-src/sys/kern/gendevcalls.awk

## Purpose
AWK generator for device call definition files, producing C header fragments with argument structures, binding unions, string macros, and invoke macros.

## Main Interfaces
- `emit_binding(field)` emits a generic binding union plus optional typed binding data.
- `emit_name_macro()` emits `<CALL>_STR`.
- `emit_invoke_macro(field, marg, carg)` emits a compound-literal macro used to invoke a device call.
- `start_decl(arg)` validates declaration state and enforces subsystem-prefixed call names.
- Main pattern rules parse a `subsystem ...;` declaration, call declarations with argument blocks, and call declarations without arguments.
- `END` validates final parser state and emits the header guard close.

## Dependencies
Consumes a specific device-call DSL and emits headers that include `<sys/device.h>` for `struct device_call_generic`.

## Implementation Notes
The generator tracks explicit parser states: expecting subsystem, expecting declaration start, and expecting declaration end. It also converts hyphenated names to underscore C identifiers and uppercase macro names.

## Research Notes
The script is small but strict: malformed declaration order, missing subsystem prefixes, unexpected braces, or unterminated declarations terminate generation with diagnostics. Generated code stability depends on the input DSL preserving the expected first-line version marker and syntax.
