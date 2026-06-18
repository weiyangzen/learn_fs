# sources/sync-backup/git-crypt/gpg.cpp

Purpose: GPG command wrapper for looking up public keys, listing secret keys, extracting UIDs, and encrypting/decrypting git-crypt key files.

Important APIs/types/functions: `gpg_get_executable`, `gpg_nth_column`, `gpg_get_uid`, `gpg_lookup_key`, `gpg_list_secret_keys`, `gpg_encrypt_to_file`, and `gpg_decrypt_from_file`.

Control flow: `gpg_get_executable` prefers Git config `gpg.program` and falls back to `gpg`. Lookup/list functions run GPG with `--batch`, `--with-colons`, and fingerprint/list flags, then parse colon-separated records. Encryption runs `gpg --batch`, optionally `--trust-model always`, writes to the target file for a recipient fingerprint, and streams plaintext via stdin. Decryption runs `gpg -q -d` and writes plaintext to an output stream.

State/persistence behavior: persistent output is GPG-encrypted key files written by `gpg_encrypt_to_file`. Other state is subprocess output and parsed fingerprint lists. GPG keyrings and trust databases are external persistent dependencies.

Dependencies/integration: uses `exec_command`, `exec_command_with_input`, `get_git_config`, and `Gpg_error`. `commands.cpp` uses these helpers for `unlock` and `add-gpg-user`.

Risks/test signals: colon output parsing assumes specific GPG record layouts and fingerprint column positions. Trust behavior differs with `--trusted` and user GPG configuration. Tests should cover configured `gpg.program`, no key/multiple key lookup, secret key listing, UID extraction, encryption/decryption round trip, and GPG failure propagation.
