# sources/security-integrity/fsverity-utils/lib/lib_private.h

Purpose: This private library header shares internal declarations, exported-symbol annotations, allocation helpers, hash algorithm structures, error reporting, and utility prototypes across `libfsverity` implementation files.

Important APIs and types: It defines `struct fsverity_hash_alg`, `struct hash_ctx`, `LIBEXPORT`, allocation wrappers such as `libfsverity_zalloc`, error-message helpers, memory-zero checks, hash helpers, and internal algorithm lookup by number.

Control flow and state: No runtime control flow exists in the header, but its declarations define how implementation files exchange state and callbacks.

Dependencies and integration points: Included by digest, signing, enabling, hash, and utils implementations. It is intentionally not public ABI, unlike `include/libfsverity.h`.

Risks and test signals: Internal API drift can break implementation consistency without downstream ABI changes. Visibility macros are sensitive for shared-library exports. Signals include clean shared/static library builds and symbol export checks.
