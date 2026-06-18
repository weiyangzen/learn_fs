# sources/security-integrity/fsverity-utils/include/libfsverity.h

Purpose: This is the public C API for `libfsverity`, exposing digest computation, PKCS#7 signing, fs-verity enablement, and hash algorithm lookup to external callers.

Important APIs and types: It defines version macros, hash constants, `struct libfsverity_merkle_tree_params`, `struct libfsverity_digest`, `struct libfsverity_signature_params`, metadata callbacks, `libfsverity_read_fn_t`, `libfsverity_compute_digest`, `libfsverity_sign_digest`, `libfsverity_enable`, `libfsverity_enable_with_sig`, `libfsverity_find_hash_alg_by_name`, and digest-size lookup.

Control flow and state: Callers provide zero-initialized parameter structs. The library allocates returned digest/signature buffers, and callers free them. Reserved fields are part of forward-compatibility validation.

Dependencies and integration points: Used by CLI commands, tests, downstream applications, pkg-config consumers, and kernel-compatible metadata tooling.

Risks and test signals: ABI stability is critical. Reserved fields, version checks, ownership rules, and nullable callback semantics must remain stable. Signals include public header compile tests, digest vector tests, signing tests, and pkg-config installation checks.
