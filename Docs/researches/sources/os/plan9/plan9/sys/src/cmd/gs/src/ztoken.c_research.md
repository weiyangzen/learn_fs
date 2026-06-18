# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztoken.c

## Purpose
Implements token-reading operators and scanner continuation support for files, strings, executable token streams, and comment callbacks.

## Public Surface
- `ztoken`: implements `token` for files and strings.
- `ztokenexec`: reads a token from a file and executes/interprets it like the interpreter, with literal procedures preserved.
- `ztokenexec_continue`: exported continuation used by interpreter refill handling.
- `ztoken_handle_comment`: handles `%ProcessComment` and `%ProcessDSCComment` callouts.
- `ztoken_scanner_options`: updates cached scanner option bits from user parameters.
- Registered through `ztoken_op_defs`.

## Implementation Notes
- File tokenization initializes `scanner_state` and uses `scan_token`.
- String tokenization uses `scan_string_token`; on error it restores the operand stack to its original depth.
- Refill handling stores scanner state and continuation on the execution stack.
- `token_continue` temporarily removes the source file from the operand stack while scanning procedures.
- `tokenexec_continue` places scanned executable objects on the execution stack, except procedures are treated as literals.
- Comment handling dynamically looks up `%ProcessComment` or `%ProcessDSCComment`, pushes file/comment operands when available, and schedules continuation.
- Scanner options map `ProcessComment`, `ProcessDSCComment`, `PDFScanRules`, and `PDFScanInvNum`.

## Dependencies
Depends on scanner/token APIs (`iscan.h`, `itoken.h`), streams/files, dictionary lookup, operand and execution stacks, filters, and name lookup.

## Risks and Notes
- Stack cleanup around scanner errors is important because procedure scanning may leave partial operands.
- Continuation memory ownership differs for saved vs reused scanner states.
- Comment callbacks mutate both operand and execution stacks and are sensitive during initialization.
- Filesystem relevance: indirect only; tokenization can read from file streams.
