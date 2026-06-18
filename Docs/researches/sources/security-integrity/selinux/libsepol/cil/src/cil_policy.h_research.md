# sources/security-integrity/selinux/libsepol/cil/src/cil_policy.h

## Purpose
`cil_policy.h` declares the textual policy serializer for a resolved CIL database.

## Important APIs, Types, And Functions
It declares `cil_gen_policy(FILE *out, struct cil_db *db)`.

## Control Flow
The header has no executable flow. The implementation traverses the database/AST and writes kernel policy statements to `FILE *`.

## State And Persistence Behavior
No state is owned here. The serializer writes to caller-owned output and reads the post-processed database.

## Dependencies And Integration Points
It includes `cil_internal.h` for `struct cil_db`. Public CIL code calls it when textual policy output is requested.

## Risks And Edge Cases
Callers must invoke it only after successful post-processing; unresolved expressions or unsorted context arrays can produce incorrect output.

## Test Signals
Compile coverage and golden textual-policy output tests are the primary signals.
