# sources/user-network-fs/mergerfs/src/strvec.hpp

## Purpose
Defines the common `StrVec` alias.

## Important APIs, Types, and Functions
`typedef std::vector<std::string> StrVec;` standardizes string-vector usage in older code.

## Control Flow
No runtime control flow exists.

## State and Persistence Behavior
No state is stored by the header itself.

## Dependencies and Integration Points
Used by config, policy, and parser code expecting `StrVec`.

## Risks and Edge Cases
As a typedef, it cannot be forward declared as a distinct type and offers no semantic constraints.

## Test Signals
Build coverage is sufficient; behavior is inherited from `std::vector<std::string>`.
