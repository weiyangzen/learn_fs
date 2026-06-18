# sources/sync-backup/git-crypt/gpg.hpp

Purpose: declares the GPG integration surface used by git-crypt command logic.

Important APIs/types/functions: `struct Gpg_error`, `gpg_get_uid`, `gpg_lookup_key`, `gpg_list_secret_keys`, `gpg_encrypt_to_file`, and `gpg_decrypt_from_file`.

Control flow: no implementation flow; callers receive vectors of fingerprints or exceptions on unrecoverable GPG failures.

State/persistence behavior: declared functions may read GPG keyrings and write/read encrypted key files, but the header itself has no state.

Dependencies/integration: includes `<string>`, `<vector>`, and `<cstddef>`. Used by `commands.cpp` and caught by `git-crypt.cpp`.

Risks/test signals: API exposes only fingerprints and raw stream encryption/decryption, so higher-level code must validate key names and key file contents. Tests should assert `Gpg_error` messages are surfaced cleanly by the CLI.
