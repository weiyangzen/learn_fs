# sources/user-network-fs/rclone/backend/crypt/crypt_internal_test.go

Purpose: Provides package-internal tests for `crypt.Fs` behavior that cannot be verified through the public fstests alone, especially encrypted `ObjectInfo` metadata and hash computation.

Important APIs, types, and functions: `makeTempLocalFs` creates and cleans a temporary local backend; `uploadFile` writes test objects; `testObjectInfo` validates `Fs.newObjectInfo`; `testComputeHash` validates `Fs.ComputeHash`; `(*Fs).InternalTest` plugs these checks into `fstests.Run`.

Control flow: Tests upload plaintext to a temporary local remote, encrypt equivalent data with the target crypt cipher to capture the expected nonce and encrypted bytes, then wrap both normal and `fs.OverrideRemote` object infos. `testComputeHash` uploads the same contents to local and crypt remotes, reads the nonce from the encrypted object via `ComputeHash`, and compares the recomputed encrypted hash with the underlying remote object's hash.

State and persistence behavior: Temporary local files are created per test and removed through `t.Cleanup`. The tests rely on crypt upload nonce state and the wrapped remote's hash support but do not mutate global configuration.

Dependencies and integration points: Uses rclone `fs`, `object`, `hash`, random data helpers, and testify. The `InternalTest` method is discovered by fstests as a backend-specific extension point.

Risks: Hash checks skip if the wrapped remote reports no hashes, so some backends only cover ObjectInfo behavior. The tests intentionally reach into unexported cipher/encrypter details, making them sensitive to crypt internals.

Test signals: Passing tests show encrypted source size is adjusted, remote names are encrypted, local encrypted hashes can be supplied for uploads, override wrappers are unwrapped, and `ComputeHash` matches the stored encrypted object hash.
