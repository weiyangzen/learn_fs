<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha-private.h -->
# sources/user-network-fs/libsmb2/lib/sha-private.h

## Purpose

`sha-private.h` provides shared boolean functions used by the bundled RFC 4634 SHA implementations. It keeps the SHA round functions in one place for SHA-1, SHA-256, and SHA-512 variants.

## Important APIs, Types, And Functions

It defines macros `SHA_Ch`, `SHA_Maj`, and `SHA_Parity`. `SHA_Ch` and `SHA_Maj` have standard FIPS forms by default and alternative equivalent forms when `USE_MODIFIED_MACROS` is defined.

## Control Flow

There is no runtime control flow. The macros are expanded inside compression loops in `sha1.c`, `sha224-256.c`, and the non-32-bit path of `sha384-512.c`. The 32-bit-only SHA-512 path undefines and redefines compatible macro names with output parameters.

## State And Persistence Behavior

No state is stored. Macro choice is compile-time only.

## Dependencies And Integration Points

The header is included after `sha.h` by each SHA implementation. It assumes inputs are integer words of the width expected by the including file.

## Risks And Edge Cases

Macro arguments are evaluated multiple times in the default forms, so callers must pass side-effect-free expressions. Any future change must preserve bit-exact FIPS behavior across 32-bit and 64-bit implementations.

## Test Signals

Known-answer tests for SHA-1, SHA-256, SHA-384, and SHA-512 should be run with and without `USE_MODIFIED_MACROS` to validate equivalence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha-private.h -->
