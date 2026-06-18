<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/usha.c -->
# sources/user-network-fs/libsmb2/lib/usha.c

Purpose: Provides a unified dispatch layer over enabled SHA implementations from RFC 4634 style code.

Important APIs, types, and functions: Exports `USHAReset`, `USHAInput`, `USHAFinalBits`, `USHAResult`, `USHABlockSize`, `USHAHashSize`, and `USHAHashSizeBits` over `USHAContext` and `enum SHAversion`.

Control flow: Each function switches on the selected SHA version in the context or parameter and forwards to SHA1, SHA224, SHA256, SHA384, or SHA512 routines depending on compile-time feature macros. Unsupported versions return `shaBadParam`; NULL contexts return `shaNull` for context-taking functions.

State and persistence behavior: State lives in the caller-provided `USHAContext`; this file only selects the concrete algorithm context inside the union.

Dependencies and integration points: Depends on `sha.h` and compile-time `USE_SHA*` macros. Used by cryptographic code that wants algorithm-neutral SHA handling.

Risks: Default size queries return SHA512 sizes for unknown algorithms rather than an error, which can hide invalid enum use. Builds with only SHA256 enabled still expose generic names that may surprise callers expecting all algorithms.

Test signals: Indirect cryptographic coverage from signing/encryption tests; no USHA-specific vector test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/usha.c -->
