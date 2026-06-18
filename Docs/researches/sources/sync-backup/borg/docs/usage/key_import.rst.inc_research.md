# sources/sync-backup/borg/docs/usage/key_import.rst.inc

Purpose: Documents `borg key import`, which restores a key previously produced by `borg key export`.

Important APIs/types/functions: CLI contract is `borg [common options] key import [options] [PATH]`. It supports `PATH`, `-` for stdin, and `--paper` for interactive import of the paper format.

Control flow: At documentation time, parser data is rendered into HTML/LaTeX option blocks plus explanatory epilog. At runtime, import reads a key backup from the path/stdin or interactively line-by-line for paper format, validates plausibility, and writes the key to the selected key destination.

State and persistence: For keyfile encryption, write location is controlled first by non-empty `BORG_KEY_FILE`, otherwise by an existing associated key in `BORG_KEYS_DIR`, otherwise by creating a new file in `BORG_KEYS_DIR`. Import can overwrite existing key files.

Dependencies and integration points: Strongly coupled to `key export`, keyfile repository modes, and environment variable docs. It also indirectly depends on repository identity matching used to find associated keys.

Risks: Overwriting the wrong key file via `BORG_KEY_FILE` or `BORG_KEYS_DIR` can disrupt repository access. Paper mode forbids `PATH`, so documentation and parser must agree to avoid ambiguous input behavior.

Test signals: Round-trip export/import tests should cover file path, stdin, `BORG_KEY_FILE`, existing and missing `BORG_KEYS_DIR` keys, and paper import validation failures.
