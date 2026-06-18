## sources/test-tools/syzkaller/prog/validation.go

Purpose: validates in-memory program graph integrity, type/direction correctness, resource references, pointer bounds, argument sizes, and conditional-union completion.

Important APIs/types/functions: package `debug`, `Prog.debugValidate`, `Prog.validate`, `validCtx`, `validationOptions`, `validateWithOpts`, `validateCall`, `validateRet`, `validateArg`, and per-arg `validate` methods.

Control flow: validation walks calls in order, verifies metadata and call properties, validates each argument against expected type and direction, checks conditional fields, validates returns, then confirms every resource use references an in-tree arg. Each concrete arg validator enforces type-specific invariants.

State and persistence: reads program state and builds local `args` and `uses` maps. Debug validation is enabled for test binaries through `os.Args[0]` suffix.

Dependencies/integration: used after mutation, builder finalization, fuzzing, and tests. Depends on target special pointer ranges, `escapingFilename`, and conditional-field checking.

Risks: validation is intentionally strict except for unsafe programs. Pointer arithmetic must account for unsafe data-mmap surrounding pages. ANY pointers are allowed unless the call has `NoSquash`.

Test signals: many tests trigger debug validation; fuzz tests intentionally panic on invariant failures.
