# sources/storage-engines/foundationdb/bindings/c/test/mako/operations.cpp

## Purpose
`operations.cpp` defines the executable operation table for Mako workloads. Each `OpKind` maps to a display name, one or two steps, a step kind, a callable that performs the C++ FDB operation, an optional post-step result decoder, and a flag indicating whether the operation requires a later commit.

## Important APIs, Types, and Functions
- `opTable` is a `std::array<Operation, MAX_OP>` and is the central dispatch table consumed by `runOneTransaction`.
- Read operations include `GRV`, `GET`, `GETRANGE`, `SGET`, `SGETRANGE`, and `STATUSJSON`.
- Write operations include `UPDATE`, `INSERT`, `INSERTRANGE`, `OVERWRITE`, `CLEAR`, `SETCLEAR`, `CLEARRANGE`, and `SETCLEARRANGE`.
- Abstract entries `COMMIT` and `TRANSACTION` exist for measurement only.

## Control Flow
`runOneTransaction` gets the current `Operation` and invokes `stepFunction(step)`. Immediate writes return an empty `Future`; reads return typed futures erased to a generic `Future`; commit steps call `tx.commit()`. Post-step functions decode futures to force result materialization. Multi-step operations such as `UPDATE`, `SETCLEAR`, and `SETCLEARRANGE` use the first step to read or commit setup state and the second step to mutate using preserved keys.

## State and Persistence Behavior
The table itself is immutable process state. It drives FDB transaction mutations and reads. Some operations mutate the provided reusable key/value buffers. Write operations persist data only if the containing transaction later commits or if their step kind commits immediately.

## Dependencies and Integration Points
It depends on `operations.hpp`, `mako.hpp`, `logger.hpp`, `utils.hpp`, the `fdb` wrapper, and operation ids from `mako.hpp`. Key generation relies on `randomString`, `numericWithFill`, and `KEY_PREFIX`. Range reads use `args.streaming_mode` and transaction spec range/reverse flags.

## Risks
The `opTable` order must match `OpKind` exactly. A visible bug risk is that `SGETRANGE` checks `args.txnspec.ops[OP_GETRANGE][OP_REVERSE]` instead of `OP_SGETRANGE`, which may make snapshot range reverse settings inconsistent. Multi-step writes rely on key buffer preservation across steps and retries. Range insertion uses asserts for positive range rather than runtime errors.

## Test Signals
Transaction-spec tests should cover every operation token, forward/reverse range reads, snapshot reads, multi-step set/clear operations, commit-needed operations, and report stats for abstract commit/transaction rows. A targeted regression should check `sgr` reverse behavior.
