# sources/user-network-fs/mergerfs/src/to_neg_errno.hpp

## Purpose
Normalizes C/POSIX return values to mergerfs negative-errno style.

## Important APIs, Types, and Functions
Two templated `to_neg_errno()` overloads return `-errno_` when `rv_ == -1`, otherwise the original return value. The one-argument overload captures global `errno`.

## Control Flow
Each helper is a simple conditional expression.

## State and Persistence Behavior
No state is changed. The one-argument form reads `errno`.

## Dependencies and Integration Points
Used by low-level filesystem wrappers to present consistent negative errors to policy and FUSE code.

## Risks and Edge Cases
Callers must call the one-argument overload before any intervening operation changes `errno`. It only treats `-1` as failure, which matches POSIX but not every API.

## Test Signals
Unit tests should cover success values, zero, `-1` with explicit errno, and errno preservation timing.
