# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/macros.h

## Purpose
Collects portability and class-shape macros such as copy/assignment suppression and compiler-specific annotations. This specific file has 30 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_MACROS_H_`, `DISALLOW_COPY_AND_ASSIGN`, `UNUSED`, `WARN_UNUSED_RESULT`. CMake commands used here include `Class`.

## Control Flow
The header is compile-time only: macros expand at class declarations or compiler-specific locations and introduce no runtime flow.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Macro misuse can hide copy semantics or compiler differences; changes have wide compile-time blast radius.

## Test Signals
Build coverage across compilers is the primary signal; class copy-suppression macros should be checked by compile-fail or static assertions where practical.
