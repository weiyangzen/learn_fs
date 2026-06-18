# sources/sync-backup/syncthing/cmd/syncthing/decrypt/decrypt.go

Purpose: implements `syncthing decrypt`, which decrypts or verifies files from an encrypted folder using the folder password and encrypted metadata trailers.

Important APIs/types/functions: `CLI`, `storedEncryptionToken`, `Run`, `walk`, `withContinue`, `getFolderID`, `process`, `decryptFile`, and `loadEncryptedFileInfo`.

Control flow: `Run` validates mode, sets the default token path, discovers folder ID from token when needed, derives the folder key, and walks the encrypted folder. `process` skips non-regular/internal files, loads encrypted `FileInfo` trailer, decrypts metadata, creates destination directories/files when decrypting, decrypts each block, verifies size and hash, writes plaintext blocks, applies permissions and modtime, and deletes partial output on failure. `--verify-only` passes a nil writer and validates without writing.

State and persistence: reads encrypted folder files and token JSON. In decrypt mode, writes plaintext files under `--to`, preserves selected permission bits, and sets modification times.

Dependencies/integration: depends on generated BEP protobufs, Syncthing config constants, filesystem abstraction, OS filename normalization, protocol encryption helpers, and scanner hash validation.

Risks and test signals: wrong password/folder ID causes metadata or block decryption failure. `--continue` logs and continues, but partial outputs are removed on file errors. Large files allocate per encrypted block. No tests in this subset cover decrypt paths.
