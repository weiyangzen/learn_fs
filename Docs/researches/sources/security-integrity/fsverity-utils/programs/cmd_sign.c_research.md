# sources/security-integrity/fsverity-utils/programs/cmd_sign.c

Purpose: This CLI command computes a file digest and writes a PKCS#7 fs-verity signature suitable for kernel built-in verification.

Important APIs and functions: `fsverity_cmd_sign()` parses digest tree options plus certificate/key or PKCS#11 parameters, computes the digest with `libfsverity_compute_digest`, signs it with `libfsverity_sign_digest`, and writes DER bytes to the output file.

Control flow and state: Command state includes tree params, signature params, opened file descriptors, allocated digest, allocated signature, and output write status. It enforces argument validity before expensive crypto operations.

Dependencies and integration points: Connects digest computation, OpenSSL signing, CLI parameter parsing, and later `cmd_enable --signature` use.

Risks and test signals: Risks include mismatched digest params between signing and enabling, sensitive key handling, PKCS#11 availability, and output file overwrite semantics. Signals include sign/verify known-key tests and negative cases for missing cert/key.
