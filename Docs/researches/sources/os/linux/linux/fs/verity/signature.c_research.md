# File Research: sources/os/linux/linux/fs/verity/signature.c

## Purpose
Implements optional fs-verity builtin PKCS#7 signature verification against the `.fs-verity` keyring.

## Main Functions
- `fsverity_verify_signature()`: validates a file’s builtin signature over its formatted fs-verity file digest, enforces `require_signatures`, reports failures, and exposes valid signatures to LSMs.
- `fsverity_init_signature()`: allocates the `.fs-verity` keyring owned by root.
- Global `fsverity_require_signatures`: sysctl-controlled policy requiring signatures on all verity files.

## Important Design Points
- Signatures are checked whenever present, even if `require_signatures` is false, because LSMs rely on this behavior.
- If the keyring is empty, signed files are rejected with `-ENOKEY` without invoking the PKCS#7 parser.
- Formatted signed digest includes magic `"FSVerity"`, fs-verity hash algorithm number, digest size, and file digest.
- Valid signature bytes are passed to `security_inode_setintegrity()` with `LSM_INT_FSVERITY_BUILTINSIG_VALID`.

## Cross-File Relationships
- Called by `fsverity_create_info()` in `open.c`.
- Initialized from `init.c`.
- Sysctl registration for `require_signatures` is in `init.c`.

## Risks / Review Notes
- This is policy/security-sensitive; comments explicitly warn to discuss behavior changes with LSM maintainers.
- Keyring permissions allow root modification unless root restricts the keyring.
- Empty-keyring short-circuit reduces PKCS#7 attack surface.
