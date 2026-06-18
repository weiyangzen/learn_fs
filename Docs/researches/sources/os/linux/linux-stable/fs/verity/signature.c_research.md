# File Research: sources/os/linux/linux-stable/fs/verity/signature.c

Implements optional fs-verity builtin signature verification. It maintains the root-owned `.fs-verity` keyring and the sysctl-backed `fsverity_require_signatures` flag.

`fsverity_verify_signature()` accepts unsigned files unless signatures are required. For signed files, it rejects verification if the keyring is empty to avoid exposing PKCS#7 parsing attack surface unnecessarily. It formats the fs-verity file digest with `"FSVerity"` magic, algorithm id, digest size, and digest bytes, then verifies the PKCS#7 signature against the keyring. It logs specific errors for missing certs, rejected signatures, malformed signatures, and other verification failures.

On success it calls `security_inode_setintegrity()` with `LSM_INT_FSVERITY_BUILTINSIG_VALID` so LSMs can consume the validated signature. `fsverity_init_signature()` allocates the keyring at boot and panics if allocation fails.
