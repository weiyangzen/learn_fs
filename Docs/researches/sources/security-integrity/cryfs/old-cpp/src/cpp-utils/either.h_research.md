# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/either.h

## Purpose
Provides a small CryFS C++ utility component. This specific file has 242 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Left`, `Right`, `either`, `Head`, `class`. Macros/constants: `MESSMER_CPPUTILS_EITHER_H`. Important declarations or call sites include `: _side(Side::left) {`; `_construct_left(std::forward<Head>(construct_left_head_arg), std::forward<Tail>(construct_left_tail_args)...);`; `: _side(Side::right) {`; `_construct_right(std::forward<Head>(construct_right_head_arg), std::forward<Tail>(construct_right_tail_args)...);`; `: _side(rhs._side) {`; `if(_side == Side::left) {`; `_construct_left(rhs._left);  // NOLINT(cppcoreguidelines-pro-type-union-access)`; `_construct_right(rhs._right);  // NOLINT(cppcoreguidelines-pro-type-union-access)`; `: _side(rhs._side) {`; `if(_side == Side::left) {`. CMake commands used here include `either`, `_construct_left`, `_construct_right`, `if`, `_destruct`, `new`. Primary includes/dependencies visible in the file include `boost/optional.hpp`, `iostream`, `assert/assert.h`.

## Control Flow
Control flow is local to the inline helpers or small translation unit and follows the surrounding cpp-utils conventions.

## State and Persistence Behavior
State behavior follows the directly visible member fields and is process-local unless delegated to filesystem/system APIs.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `boost/optional.hpp`, `iostream`, `assert/assert.h`.

## Risks and Edge Cases
Risks are local and should be tested through the module that consumes this helper.

## Test Signals
Use focused unit tests at the consuming module boundary.
