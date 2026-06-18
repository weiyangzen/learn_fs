# File Research: sources/os/bsd/netbsd-src/sys/sys/psref.h

## Purpose
Declares passive reference tracking for objects that can be referenced without heavy locking while supporting controlled draining/destruction.

## Main API
- Structures: `struct psref_target`, `struct psref`, opaque `struct psref_class`.
- Initialization: `psref_init`, `psref_class_create`, `psref_class_destroy`, `psref_target_init`, `psref_target_destroy`.
- Reference operations: `psref_acquire`, `psref_release`, `psref_copy`.
- Assertion helper: `psref_held`.
- Debug hooks/macros when `PSREF_DEBUG` is enabled.

## Dependencies
Includes optional debug config, basic types, and `sys/queue.h`.

## Risks and Notes
`prt_draining` is written only once to block new references during destruction. `struct psref` is per-reference, CPU-local bookkeeping; callers must observe CPU and lifetime rules implemented by the psref subsystem.
