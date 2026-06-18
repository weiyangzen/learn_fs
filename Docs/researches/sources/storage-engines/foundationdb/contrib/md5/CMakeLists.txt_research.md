# sources/storage-engines/foundationdb/contrib/md5/CMakeLists.txt

## Purpose
This CMake file builds the vendored MD5 implementation used by FoundationDB when OpenSSL MD5 is not selected.

## Important APIs, Types, And Functions
It declares `add_library(md5 STATIC md5.c)`, disables clang-tidy, and publishes `include` as a public target include directory.

## Control Flow
CMake compiles `md5.c` into a static library and exposes `include/md5/md5.h` to consumers.

## State And Persistence Behavior
Only build graph state is affected. Runtime digest state is in `MD5_CTX`.

## Dependencies And Integration Points
It integrates a public-domain MD5 implementation into the parent build. Consumers link the `md5` target and include `md5/md5.h`.

## Risks And Edge Cases
MD5 is cryptographically broken and should only be used for compatibility/non-security checksums. Build selection with `HAVE_OPENSSL` affects whether this implementation or OpenSSL declarations are used.

## Test Signals
Build tests should verify the target compiles with and without OpenSSL configuration and that known MD5 vectors link and pass.
