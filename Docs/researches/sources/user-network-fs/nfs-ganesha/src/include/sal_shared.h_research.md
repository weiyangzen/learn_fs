# sources/user-network-fs/nfs-ganesha/src/include/sal_shared.h

## Purpose
This small shared SAL header defines the common state type enumeration without pulling in the full SAL data model.

## Important APIs, Types, And Control Flow
`enum state_type` includes none, NFSv4 share, delegation, byte-range lock, layout, NLM lock, NLM share, 9P fid, and max sentinel values.

## State And Persistence
There is no runtime state. Values are stored in `state_t` and drive type-specific interpretation of `union state_data`.

## Dependencies And Integration Points
It is included by `sal_data.h` and any code that needs state type labels while avoiding circular dependencies.

## Risks And Test Signals
Changing enum values can break persisted/debug assumptions and switch statements. Test signals include exhaustive switch warnings, state allocation/deletion paths for every type, and metrics/log formatting that maps each state type.
