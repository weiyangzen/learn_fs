# sources/user-network-fs/rclone/fs/config/crypt.go

Purpose: handles encrypted rclone config files, password acquisition, encryption/decryption, password key derivation, and password change/remove workflows.

Important APIs/functions: global `configKey`, `PasswordPromptOutput`, and `PassConfigKeyForDaemonization`. Public functions include `IsEncrypted`, `Decrypt`, `GetPasswordCommand`, `Encrypt`, `SetConfigPassword`, `ClearConfigPassword`, `ChangeConfigPasswordAndSave`, and `RemoveConfigPasswordAndSave`. Internal helpers include `getConfigPassword` and `changeConfigPassword`.

Control flow: `Decrypt` scans to the first non-empty non-comment line. Plaintext is returned as-is, including non-seekable stream recovery with `io.MultiReader`; unsupported encryption versions error. For encrypted configs it obtains a key from `--password-command`, `RCLONE_CONFIG_PASS`, `_RCLONE_CONFIG_KEY_FILE`, or interactive prompt, then base64-decodes secretbox ciphertext, extracts nonce, and retries prompts until secretbox opens. `Encrypt` passes plaintext through when no key is set; otherwise it writes a marker header, random nonce, and base64-encoded NaCl secretbox output. `SetConfigPassword` validates/normalizes via `checkPassword`, hashes `[` + password + `][rclone-config]` with SHA-256, and optionally writes an obscured key temp file for daemonized child processes.

State and persistence behavior: `configKey` is process-global and controls future saves. `_RCLONE_CONFIG_KEY_FILE` handoff deletes the temp file after reading. Password changes update `configKey` then call `SaveConfig`; removal clears the key and saves plaintext.

Dependencies and integration points: depends on `fs.ConfigInfo` for `AskPassword` and `PasswordCommand`, UI password functions, `obscure`, `secretbox`, base64, OS env/temp files, and configfile storage's `Decrypt`/`Encrypt` calls.

Risks: config encryption depends on global mutable key state, so tests and long-running processes must clear or set it deliberately. `Decrypt` can prompt interactively in loops unless disabled by config. Temp key file handling must avoid leaving key material behind on errors. Tokens/passwords may appear in subprocess command output if password command is misconfigured.

Test signals: `crypt_internal_test.go` covers password validation/normalization and password-command change flow; broader crypt tests outside this subset likely cover encrypt/decrypt round trips and password command errors.
