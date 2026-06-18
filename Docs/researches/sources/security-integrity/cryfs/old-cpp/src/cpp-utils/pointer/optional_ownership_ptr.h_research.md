# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/optional_ownership_ptr.h

## Purpose
Defines ownership pointer adapters and casts used in old CryFS C++ code before newer standard-library facilities were fully available. This specific file has 50 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_POINTER_OPTIONALOWNERSHIPPOINTER_H_`. Important declarations or call sites include `optional_ownership_ptr<T> WithOwnership(std::unique_ptr<T> obj) {`; `auto deleter = obj.get_deleter();`; `return optional_ownership_ptr<T>(obj.release(), deleter);`; `optional_ownership_ptr<T> WithOwnership(unique_ref<T> obj) {`; `return WithOwnership(static_cast<std::unique_ptr<T>>(std::move(obj)));`; `optional_ownership_ptr<T> WithoutOwnership(T *obj) {`; `return optional_ownership_ptr<T>(obj, [](T*){});`; `optional_ownership_ptr<T> null() {`; `return WithoutOwnership<T>(nullptr);`. Primary includes/dependencies visible in the file include `unique_ref.h`, `functional`.

## Control Flow
Pointer helpers transfer or observe ownership, perform checked casts, and provide compatibility shims where old compilers or Boost containers had limitations.

## State and Persistence Behavior
Ownership wrappers store raw or smart pointers in memory and encode whether ownership is held by the wrapper.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `unique_ref.h`, `functional`.

## Risks and Edge Cases
Optional ownership and cast helpers can make lifetime/cast assumptions non-obvious. Failed dynamic moves must leave ownership in a well-defined state.

## Test Signals
Test ownership transfer, null/empty optional ownership, successful and failed dynamic casts, unique_ref move-only behavior, and Boost optional compatibility.
