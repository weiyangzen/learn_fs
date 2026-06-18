# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnum.hh

## Purpose
Provides a macro to add bitwise operators to strongly named enum types.

## Important APIs, Types, And Functions
`XRDOUC_ENUM_OPERATORS(T)` defines inline `|`, `|=`, `&`, `&=`, `^`, `^=`, and `~` by casting enum values to `int` and back to `T`.

## Control Flow
No runtime control flow beyond inline operator evaluation.

## State And Persistence
No state.

## Dependencies And Integration Points
No dependencies. It integrates with enum flag declarations elsewhere in XRootD that need type-preserving bit operations.

## Risks And Test Signals
Risks include truncation or sign issues for enum values wider than `int`, namespace pollution if used in headers, and duplicate operator definitions if expanded multiple times for the same type in one namespace. Test signals are compile coverage for representative enum flags and static assertions where wide values are possible.
