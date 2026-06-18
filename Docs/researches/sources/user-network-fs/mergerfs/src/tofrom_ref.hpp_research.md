# sources/user-network-fs/mergerfs/src/tofrom_ref.hpp

## Purpose
Provides a `ToFromString` adapter around a mutable reference and conversion functors.

## Important APIs, Types, and Functions
`TFSRef<T>` stores `T& value`, a `FromFunc`, and a `ToFunc`. `to_string()` calls the to functor; `from_string()` calls the from functor and writes back to `value`.

## Control Flow
Construction captures references and functions. Conversion calls are direct and return the parser's status.

## State and Persistence Behavior
The wrapper mutates the referenced variable but owns no persistent storage.

## Dependencies and Integration Points
Depends on `tofrom_string.hpp`, `string_view`, and functional conversion code used by runtime options.

## Risks and Edge Cases
The referenced object must outlive the wrapper. Parser failures must leave the referenced value in a defined state according to the supplied functor.

## Test Signals
Test successful conversion, parser error propagation, referenced-value mutation, and lifetime assumptions in option registration.
