# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/cast.h

## Purpose
Defines ownership pointer adapters and casts used in old CryFS C++ code before newer standard-library facilities were fully available. This specific file has 26 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_POINTER_CAST_H_`. Important declarations or call sites include `inline std::unique_ptr<DST> dynamic_pointer_move(std::unique_ptr<SRC> &source) {`; `DST *casted = dynamic_cast<DST*>(source.get());`; `if (casted != nullptr) {`; `std::ignore = source.release();`; `return std::unique_ptr<DST>(casted);`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `memory`.

## Control Flow
Pointer helpers transfer or observe ownership, perform checked casts, and provide compatibility shims where old compilers or Boost containers had limitations.

## State and Persistence Behavior
Ownership wrappers store raw or smart pointers in memory and encode whether ownership is held by the wrapper.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `memory`.

## Risks and Edge Cases
Optional ownership and cast helpers can make lifetime/cast assumptions non-obvious. Failed dynamic moves must leave ownership in a well-defined state.

## Test Signals
Test ownership transfer, null/empty optional ownership, successful and failed dynamic casts, unique_ref move-only behavior, and Boost optional compatibility.
