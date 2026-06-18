# sources/security-integrity/fscrypt/actions/config.go

## Purpose
Implements global fscrypt configuration creation and loading. It writes `ConfigFileLocation` with defaults, calibrated passphrase hashing costs, and optional policy version override, then reloads configs with missing fields filled from `metadata.Default*`.

## APIs, Types, and Control Flow
Key exports are `ConfigFileLocation`, `CreateConfigFile`, and config-related error types. `CreateConfigFile` opens the config with `O_CREATE|O_WRONLY|O_EXCL` via `filesystem.OpenFileOverridingUmask`, builds `metadata.Config`, applies a policy-version override, calls `getHashingCosts`, and writes through `metadata.WriteConfig`. `getConfig` opens and parses the protobuf/json metadata config, applies defaults for source, padding, contents, filenames, and policy version, then validates.

Hash calibration starts with one Argon2 time pass, memory of `8 * parallelism` KiB, and effective CPU parallelism capped by `metadata.MaxParallelism`. It repeatedly doubles memory up to `memoryBytesLimit()/1024`, then doubles time, timing via process CPU time divided by parallelism, and linearly interpolates between the last two cost points.

## State, Dependencies, and Integration
Persistent state is `/etc/fscrypt.conf` by default, overridable in tests and CLI via `FSCRYPT_CONF`. It depends on `metadata` for config validation and serialization, `crypto.PassphraseHash`, `cgroup` for container-aware limits, `filesystem` for umask override, and `unix` syscalls for sysinfo and CPU time.

## Risks and Test Signals
Calibration is environment-sensitive and can be slow; cgroup failures intentionally fall back to host CPU/RAM. `timeHashingCosts` assumes `costs.Parallelism` is nonzero after metadata validity constraints. Tests check config file permissions and policy-version override, while `hashing_test.go` checks calibration roughness.
