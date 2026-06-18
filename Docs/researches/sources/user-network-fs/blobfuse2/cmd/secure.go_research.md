# sources/user-network-fs/blobfuse2/cmd/secure.go
## sources/user-network-fs/blobfuse2/cmd/secure.go

Purpose: implements the `blobfuse2 secure` command group for encrypting and decrypting YAML config files with a user-provided AES passphrase.

Important APIs/types/functions: `secureOptions`, `SecureConfigEnvName`, `SecureConfigExtension`, global `secOpts`, `secureCmd`, `encryptCmd`, `decryptCmd`, `validateOptions`, `encryptConfigFile`, `decryptConfigFile`, `saveToFile`, and `init` command/flag registration.

Control flow: subcommands first call `validateOptions`, which fills `PassPhrase` from `BLOBFUSE2_SECURE_CONFIG_PASSPHRASE` if needed, requires a config path, checks file existence, and requires a passphrase. `encryptConfigFile` reads plaintext, calls `common.EncryptData`, and optionally writes the ciphertext to either `--output-file` or `$HOME/.blobfuse2/<basename>.azsec`; default encryption deletes the source. `decryptConfigFile` reads ciphertext, calls `common.DecryptData`, and optionally writes plaintext to either `--output-file` or a default path with the original extension stripped; default decryption does not delete the encrypted source. `saveToFile` writes mode `0777` and may remove `secOpts.ConfigFile`.

State and persistence: all options live in global `secOpts`, shared by secure subcommands. The command reads, writes, and sometimes deletes config files. Defaults use `common.DefaultWorkDir`, expanded with `common.ExpandPath` for encrypt and `os.ExpandEnv` for decrypt.

Dependencies/integration: Cobra, filesystem APIs, `common.EncryptData`/`DecryptData`, `common.DefaultWorkDir`, and env var passphrase support.

Risks: output files are world-writable (`0777`), risky for decrypted secrets. Default encrypt deletes the original file after write. Global `secOpts` can leak between tests/commands unless flags are reset. No key derivation is performed; the passphrase bytes must already be a valid AES key length.

Test signals: `secure_test.go` covers help, encrypt/decrypt round trips, missing config/key, nonexistent file, invalid key length, get, set, and invalid key lookup.
