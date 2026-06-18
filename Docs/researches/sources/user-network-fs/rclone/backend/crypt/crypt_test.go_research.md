# sources/user-network-fs/rclone/backend/crypt/crypt_test.go

Purpose: Runs rclone's generic filesystem test suite against the crypt backend across the main filename/data encryption configurations.

Important APIs, types, and functions: `TestIntegration` uses an externally supplied `-remote`; `TestStandardBase32`, `TestStandardBase64`, `TestStandardBase32768`, `TestOff`, `TestObfuscate`, and `TestNoDataObfuscate` build temporary local crypt configs. Each invokes `fstests.Run` with `crypt.Object` as the nil object type and declares unsupported writer/MIME methods.

Control flow: If an explicit remote is configured, only `TestIntegration` runs. Otherwise each mode creates an `ExtraConfig` crypt remote pointing to a temp directory with an obscured password and mode-specific settings. Obfuscate tests skip on macOS because generated control-character filenames conflict with the platform.

State and persistence behavior: Tests write to temp directories under `os.TempDir`; fstests owns cleanup and lifecycle. Config is injected in-memory through `ExtraConfig`, avoiding permanent rclone config mutation.

Dependencies and integration points: Imports local, drive, and swift backends for test availability, plus `fstest`, `fstests`, and `obscure`. These tests exercise crypt through the public rclone backend interface rather than package internals.

Risks: Temporary directory names are shared by some mode tests, so failed cleanup can leave residue. Generic fstests provide broad behavioral coverage but do not directly assert ciphertext layout or every optional wrapper interface.

Test signals: Coverage confirms crypt can create, list, read, update, delete, and traverse data with standard encodings, off mode, obfuscation, and no-data-encryption mode.
