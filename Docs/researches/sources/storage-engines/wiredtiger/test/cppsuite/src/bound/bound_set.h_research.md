# sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound_set.h

Purpose: Declares a helper for applying lower and upper cursor bounds together.

Important APIs/types/functions: `class bound_set` deletes the default constructor, accepts two `bound` objects or a prefix key, exposes `apply`, `get_lower`, and `get_upper`.

Control flow: callers construct a complete bound pair before application.

State and persistence: owns lower and upper `bound` objects; applying affects the target cursor's range state.

Dependencies/integration: includes `bound.h` and `scoped_cursor.h`; used by cppsuite tests that need bounded scans.

Risks and test signals: no API-level validation for lower/upper consistency. Tests must assert resulting scan contents, not just successful bound application.
