# sources/sync-backup/borg/docs/usage/key_list.rst.inc

Purpose: Documents `borg key list`, which displays repository keys and identifies the key currently used to unlock the repository.

Important APIs/types/functions: CLI contract is `borg [common options] key list [options]` with no command-specific options. Output fields are key id, mode (`repokey` or `keyfile`), label, key derivation/encryption algorithm, and a `*` marker for the active key.

Control flow: Documentation generation is straightforward parser-to-rST output. Runtime behavior is read-only: open/unlock repository, enumerate known keys, and format a list.

State and persistence: No intended mutation. It observes repository/key metadata and the active unlock key.

Dependencies and integration points: Supports `key remove --key` by exposing key IDs/prefixes, supports key administration workflows, and depends on common repository/key location handling.

Risks: Output ambiguity could cause the wrong key to be removed if IDs are truncated externally. Tests should ensure active-key marking is stable and labels/algorithms are represented.

Test signals: Parser docs regeneration plus functional tests with multiple keys, duplicate prefixes, keyfile/repokey modes, and active key selection.
