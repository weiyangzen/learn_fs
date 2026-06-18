# sources/security-integrity/selinux/libsepol/cil/src/cil_mem.h

## Purpose
`cil_mem.h` declares CIL allocation wrappers that centralize allocation failure handling.

## Important APIs, Types, And Functions
Declared functions are `cil_malloc`, `cil_calloc`, `cil_realloc`, `cil_strdup`, and printf-style `cil_asprintf`.

## Control Flow
The header itself has no executable flow. The implementation exits on allocation failure rather than returning errors.

## State And Persistence Behavior
No state is stored here. Callers receive heap memory that must be freed or transferred to CIL object destructors.

## Dependencies And Integration Points
The header is included by list, parser, lexer, logging users, post-processing, and most AST object constructors.

## Risks And Edge Cases
Consumers should not expect recoverable OOM from these APIs. The header relies on standard size and varargs declarations being available through includes in translation units.

## Test Signals
Compiler coverage of the `cil_asprintf` format attribute and allocator fault-injection tests are useful signals.
