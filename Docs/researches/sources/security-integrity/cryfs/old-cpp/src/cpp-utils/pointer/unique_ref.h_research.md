# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/unique_ref.h

## Purpose
Defines ownership pointer adapters and casts used in old CryFS C++ code before newer standard-library facilities were fully available. This specific file has 196 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `T`, `D`, `unique_ref`, `U`, `T2`, `D2`, `DST`, `SRC`, `std`, `hash`, `less`. Macros/constants: `MESSMER_CPPUTILS_POINTER_UNIQUE_REF_H`. Important declarations or call sites include `: _target(std::move(from._target)) {`; `_invariant();`; `: _target(std::move(from._target)) {`; `_invariant();`; `_target = std::move(from._target);`; `_invariant();`; `_target = std::move(from._target);`; `_invariant();`; `_invariant();`; `_invariant();`. CMake commands used here include `unique_ref`, `_invariant`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`, `if`. Primary includes/dependencies visible in the file include `memory`, `boost/optional.hpp`, `../macros.h`, `gcc_4_8_compatibility.h`, `cast.h`, `../assert/assert.h`.

## Control Flow
Pointer helpers transfer or observe ownership, perform checked casts, and provide compatibility shims where old compilers or Boost containers had limitations.

## State and Persistence Behavior
Ownership wrappers store raw or smart pointers in memory and encode whether ownership is held by the wrapper.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `memory`, `boost/optional.hpp`, `../macros.h`, `gcc_4_8_compatibility.h`, `cast.h`, `../assert/assert.h`.

## Risks and Edge Cases
Optional ownership and cast helpers can make lifetime/cast assumptions non-obvious. Failed dynamic moves must leave ownership in a well-defined state.

## Test Signals
Test ownership transfer, null/empty optional ownership, successful and failed dynamic casts, unique_ref move-only behavior, and Boost optional compatibility.
