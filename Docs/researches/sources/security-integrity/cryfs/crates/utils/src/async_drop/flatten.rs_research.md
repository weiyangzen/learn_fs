# sources/security-integrity/cryfs/crates/utils/src/async_drop/flatten.rs

Purpose: combines two fallible async-drop guard results while cleaning up any successfully created guard when the other result failed.

Important APIs/types/functions: `flatten_async_drop<E, T, E1, U, E2>(first, second)` returns both guards on dual success or an error converted into `E`.

Control flow: four match cases handle both-ok, first-ok/second-err, first-err/second-ok, and both-err. On mixed success/failure it async-drops the successful guard before returning the failure.

State/persistence: no persistent state; cleanup side effects belong to dropped guards.

Dependencies/integration: generic over `AsyncDropGuard` values and error conversions. Useful in constructors that allocate two async resources.

Risks: TODOs note error loss: if cleanup fails while returning another error, only one error is reported. When both inputs are errors, the second error is discarded.

Test signals: unit tests cover all four result combinations and verify cleanup counters.
