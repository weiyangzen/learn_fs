# sources/security-integrity/encfs/src/reverse_fs.rs

Purpose: implements `ReverseFs`, a reverse-direction FUSE filesystem that presents an encrypted virtual view over a plaintext source tree. It is the opposite of `EncFs`: callers see encrypted names and ciphertext bytes while the backing directory stores plaintext.

Important APIs/types/functions: `ReverseFs::new` captures source path, cipher, config, in-memory config bytes, and config file metadata. `ReverseFileHandle` stores an open plaintext file plus the per-file IV used for virtual encryption. `resolve_source_path` decrypts each incoming FUSE path component and tracks chained directory IV state. `ciphertext_size_for_plaintext` and `read_encrypted` use `BlockLayout` and `BlockCodec` to map plaintext file reads into virtual ciphertext ranges. `metadata_to_filetype` and `system_time_from_metadata_secs` adapt Unix metadata to `fuse_mt` structures.

Control flow: FUSE `getattr`, `readdir`, `open`, `read`, and `readlink` translate encrypted virtual paths back to source paths, then either report transformed metadata or synthesize encrypted content. `read` special-cases `/.encfs7`, otherwise clones a handle under a mutex, drops the lock, bounds the request by computed ciphertext size, and encrypts only the requested blocks. `readdir` skips source dotfiles and adds a virtual root `.encfs7`.

State and persistence: the filesystem is read-only. Persistent state remains in the plaintext source tree; runtime state is limited to a mutex-protected file-handle map and atomic handle counter. The virtual config file is backed by `config_bytes`, `config_mtime`, `config_uid`, and `config_gid`, not a source path lookup.

Dependencies and integration points: depends on `fuse_mt`, `libc`, Unix metadata extensions, `SslCipher`, `BlockLayout`, and `BlockCodec`. It integrates with the `encfsr` binary and with forward `EncFs` for round-trip validation. It assumes `unique_iv=false` for reverse mode and uses `external_iv_chaining` to choose whether directory IVs feed file IV encryption.

Risks: `resolve_source_path` uses `to_str`, so non-UTF-8 encrypted path components return `EILSEQ`; this may be acceptable for EncFS name encodings but narrows byte-path compatibility. `read_encrypted` computes `end_block` as `(offset + size - 1) / block_size`, so callers must not pass `size=0`. Dotfile skipping hides all source dotfiles, not only config files. `metadata.blocks()` is reported from plaintext metadata even when virtual ciphertext size differs. Read-only operations return `EROFS`, but xattr read/list behavior is mixed (`ENODATA`/`ENOSYS`).

Test signals: covered by `encfsr_test.rs` for CLI gating and by `encfsr_live_test.rs` for encrypted readdir, ciphertext stat size, read-only write failure, path resolution, virtual config exposure, V6/V7 round-trips, symlink target encryption, and streaming.
