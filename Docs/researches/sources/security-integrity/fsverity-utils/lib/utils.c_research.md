# sources/security-integrity/fsverity-utils/lib/utils.c

Purpose: This file implements small internal utility functions used by `libfsverity`, chiefly allocation, zeroing, error reporting, and memory inspection helpers.

Important APIs and functions: It provides `libfsverity_zalloc`, error print helpers, OpenSSL-independent memory-zero checks such as `libfsverity_mem_is_zeroed`, and other private support routines declared in `lib_private.h`.

Control flow and state: Functions are stateless except for emitting diagnostics to stderr/logging targets. Allocation returns zero-initialized memory to callers, which own and free it.

Dependencies and integration points: Used by digest, signing, and enable code. It underpins reserved-field validation and output buffer allocation for public APIs.

Risks and test signals: Allocation overflow or nonzero reserved-field checks can cause security or compatibility defects. Signals include parameter validation tests, memory sanitizer runs, and expected diagnostic paths for invalid inputs.
