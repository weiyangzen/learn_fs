# sources/user-network-fs/mergerfs/src/str.hpp

## Purpose
Declares shared string utility functions for splitting, joining, matching, trimming, case conversion, and byte/list formatting.

## Important APIs, Types, and Functions
The `str` namespace exports vector/set splitters, `splitkv`, joins for vectors and sets, `startswith`, `endswith`, `contains`, `replace_all`, trim helpers, `tolower`, `erase`, null termination, and match helpers.

## Control Flow
The header provides declarations only; callers link to `str.cpp` implementations.

## State and Persistence Behavior
The declared routines are stateless except for in-place mutation of caller strings where requested.

## Dependencies and Integration Points
Includes STL string, view, vector, set, and utility headers. Many config and path modules depend on this API.

## Risks and Edge Cases
Consumers must understand which helpers return empty tokens and which mutate inputs. API changes here have broad compile-time impact.

## Test Signals
Compile and unit coverage should include all declarations and edge string cases mirrored from `str.cpp`.
