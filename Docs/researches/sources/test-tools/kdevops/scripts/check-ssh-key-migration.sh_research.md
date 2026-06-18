# sources/test-tools/kdevops/scripts/check-ssh-key-migration.sh

Purpose: prints a migration notice when old fixed Terraform SSH keys exist but new directory-hashed keys do not.

Important APIs/types/functions: `sha256sum`, path construction in `$HOME/.ssh`, `test -f`, and heredoc output.

Control flow: computes eight-character hash from `TOPDIR_PATH`, checks old/new public key paths, and prints instructions only when migration may be needed.

State/persistence behavior: read-only; it does not move keys.

Dependencies/integration: supports upgrade flow from old kdevops key naming to hashed per-directory key naming.

Risks/test signals: hash uses raw `echo "$TOPDIR_PATH"` including newline semantics; message only checks public key existence. Test signal is notice output for old-only key state and silence otherwise.
