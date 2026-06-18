# sources/user-network-fs/mergerfs/src/tofrom_string.hpp

## Purpose
Defines the abstract interface for values that can be read from and written to strings.

## Important APIs, Types, and Functions
`ToFromString` declares pure virtual `to_string()` and `from_string(std::string_view)`. Public flags `display` and `ro` control visibility and read-only behavior in consumers.

## Control Flow
Derived classes implement conversion logic. The base class only defines the contract and default flags.

## State and Persistence Behavior
The base stores two booleans; derived wrappers may reference persistent runtime configuration.

## Dependencies and Integration Points
Used by config and control-file xattr code to expose options uniformly.

## Risks and Edge Cases
No virtual destructor is declared in this file; ownership through base pointers must be audited. Flags are mutable public data.

## Test Signals
Test derived wrappers through the base interface, display/ro handling in control surfaces, and ownership patterns.
