# sources/security-integrity/ecryptfs-utils/scripts/validate-dir.sh

Purpose: shallow safety check that the current directory looks like an ecryptfs-utils tree.

Important APIs/commands: checks marker files `AUTHORS COPYING ChangeLog INSTALL Makefile.am NEWS README THANKS configure`; exits 1 on first missing file, otherwise exits 0.

Control flow/state: read-only; prints found/missing messages.

Dependencies/integration: called before destructive cleanup by `delete-cruft.sh`.

Risks: marker-file validation can be spoofed and does not verify paths before deletion. Requires generated `configure` to exist.

Test signals: shell exit code and printed validation success.
