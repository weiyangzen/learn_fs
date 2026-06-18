# sources/sync-backup/borg/docs/usage/key_change-passphrase.rst.inc

Purpose: Documents `borg key change-passphrase`, the command that changes the passphrase protecting an encrypted Borg key. It is an auto-generated command include.

Important APIs/types/functions: The documented CLI surface is `borg [common options] key change-passphrase [options]` with no command-specific options beyond common options. It uses the generated option table/list structure supplied by the docs builder.

Control flow: Documentation generation reads the parser epilog and emits the command page. Runtime behavior described is an interactive/key-management flow: load the existing key, ask for a new passphrase, and re-protect the existing key data with the new passphrase.

State and persistence: Mutates the encrypted key wrapper/passphrase protection, but not encryption/MAC keys, chunker seed, or past/future archive cryptographic identity. Persistence is in the existing key file or repository-stored key.

Dependencies and integration points: Related to `repo-create` passphrase guidance, `key export/import`, and environment/common options for locating repositories and keys.

Risks: The main risk is false security after compromise; the document explicitly warns that changing the passphrase after both passphrase and key compromise does not secure backups using the same repository.

Test signals: Regenerate usage docs from parser help. Functional tests should confirm old passphrase rejection, new passphrase acceptance, and unchanged archive access/key IDs after passphrase change.
