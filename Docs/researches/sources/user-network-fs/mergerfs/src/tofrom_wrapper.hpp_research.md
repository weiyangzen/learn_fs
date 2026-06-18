# sources/user-network-fs/mergerfs/src/tofrom_wrapper.hpp

## Purpose
Implements mutable and read-only wrappers that expose ordinary values through the `ToFromString` interface.

## Important APIs, Types, and Functions
`ToFromWrapper<T>` stores `T value`, conversion callbacks, assignment/conversion operators, and `to_string()`/`from_string()`. `ROToFromWrapper<T>` exposes the same read path but rejects writes with `-EROFS` and marks `ro = true`.

## Control Flow
Mutable wrappers parse into `value`; read-only wrappers ignore input and return read-only errors. Operators provide ergonomic access to the contained value.

## State and Persistence Behavior
The contained value is process-live configuration state. No disk persistence is performed by the wrapper.

## Dependencies and Integration Points
Depends on `errno.hpp`, `tofrom_string.hpp`, and project conversion functions. Used for mergerfs runtime options and xattr-backed configuration.

## Risks and Edge Cases
Implicit conversions and assignment operators can hide mutation. Parser functions must validate input fully. Read-only behavior relies on consumers respecting `from_string()` errors and `ro`.

## Test Signals
Test to/from conversions, assignment operators, read-only rejection, display/ro flags, and invalid input behavior.
