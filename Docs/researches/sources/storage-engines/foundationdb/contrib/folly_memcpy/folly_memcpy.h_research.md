# sources/storage-engines/foundationdb/contrib/folly_memcpy/folly_memcpy.h

## Purpose
Header declaration for the optimized Folly memcpy symbol when supported.

## Important APIs, Types, And Functions
Under `(defined(__linux__) || defined(__FreeBSD__)) && defined(__AVX__)`, declares `extern "C" void* folly_memcpy(void* dst, const void* src, uint32_t length);`.

## Control Flow
Header-only conditional declaration.

## State And Persistence
No state.

## Dependencies And Integration
Consumers must include this in C++ builds where `uint32_t` is already available or available from included project headers; this header itself does not include `<stdint.h>`/`<cstdint>`. Links against the `folly_memcpy` target.

## Risks
The declaration guard includes FreeBSD and AVX, while assembly emits code only on Linux x86_64. Missing direct include for `uint32_t` can make standalone inclusion fragile. No fallback declaration exists for SSE2 builds even though assembly has an SSE2 path.

## Test Signals
Standalone compile test including only this header, and platform matrix tests matching CMake and assembly availability.
