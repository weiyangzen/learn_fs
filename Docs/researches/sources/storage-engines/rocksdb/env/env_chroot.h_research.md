## sources/storage-engines/rocksdb/env/env_chroot.h

### Purpose

`env/env_chroot.h` declares `ChrootFileSystem` and factory helpers for building a chroot-like RocksDB filesystem or Env on non-Windows platforms.

### Important APIs, Types, And Functions

- `ChrootFileSystem` derives from `RemapFileSystem`.
- `kClassName()`/`Name()` identify the implementation as `ChrootFS`.
- `GetTestDirectory()` and `PrepareOptions()` override filesystem behavior.
- Protected `EncodePath()` and `EncodePathWithNewBasename()` define the remapping contract.
- `NewChrootEnv()` returns an `Env*` that translates root-relative paths under `chroot_dir`.
- `NewChrootFileSystem()` returns a shared filesystem wrapper for composition.

### Control Flow

Callers construct a chroot filesystem with a base filesystem and directory, then `PrepareOptions()` canonicalizes and validates it. Remap hooks are used by inherited file operations to translate logical paths. `NewChrootEnv()` wraps the result in a `CompositeEnvWrapper` so legacy Env callers can use the remapped filesystem while retaining base env thread services.

### State And Persistence Behavior

The only declared member is `std::string chroot_dir_`. It stores the configured/canonical root. Persistent file effects happen through inherited remapped operations on the base filesystem.

### Dependencies And Integration Points

The header depends on `env/fs_remap.h` and `rocksdb/file_system.h`, and is excluded on Windows. It is implemented in `env_chroot.cc` and integrates with RocksDB's Env/FileSystem composition layer.

### Risks And Edge Cases

- Consumers must handle null returns from factory helpers when the chroot directory does not exist or cannot be prepared.
- Because the feature is not a strong security boundary, users should not rely on it for adversarial isolation.
- New remapped operations added to `RemapFileSystem` should be checked to ensure they use the correct encode hook for existing vs new paths.

### Test Signals

Compile coverage on non-Windows platforms plus path-remapping behavior tests are important. Static research only; no test command was run.
