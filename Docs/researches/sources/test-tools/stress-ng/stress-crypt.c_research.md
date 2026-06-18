# sources/test-tools/stress-ng/stress-crypt.c

## Purpose
This stressor exercises libc/libcrypt password hashing methods. It generates random salts and phrases, runs `crypt_r()` or `crypt()` for either all supported method prefixes or one selected method, tolerates unsupported algorithms, and reports per-method encryptions per second.

## Important APIs, Types, And Functions
`crypt_method_t` maps a salt prefix to a human-readable method name. `crypt_methods` includes all, bcrypt, bsdicrypt, descrypt, gost-yescrypt, MD5, NT, scrypt, SHA-1, SHA-256, SHA-512, SunMD5, and yescrypt prefixes. `stress_crypt_method()` exposes method names to option parsing. `stress_crypt_id()` times one encryption and handles unsupported `crypt` errors. `stress_crypt()` allocates metric storage, generates input strings, calls methods, updates bogo count, and emits metrics.

## Control Flow
The stressor reads `crypt-method`, allocates a metrics array, initializes `crypt_data` when using `crypt_r()`, and waits for the sync barrier. Each loop creates a random setting and phrase from the 64-character crypt alphabet. In `all` mode it iterates every method after index 0, splices the method prefix into the setting, resets `crypt_data.initialized`, and calls `stress_crypt_id()`. In single-method mode it builds one setting and calls only the selected method. Fatal unexpected crypt errors stop the loop; unsupported or invalid methods are ignored.

## State And Persistence
State is in-memory only: current phrase, current setting, optional static `struct crypt_data`, and per-method timing/count metrics. No password hashes are stored persistently. The output metrics are reported for methods that produced at least one successful result.

## Dependencies And Integration Points
The stressor is compiled only with libcrypt and either `crypt.h` or FreeBSD support. It depends on stress-ng settings, random number generation, metric helpers, and memory allocation. The method selector is wired through `OPT_crypt_method`.

## Risks
Method availability depends on libcrypt implementation and system policy, so `EINVAL`, `ENOENT`, `ENOSYS`, and `EOPNOTSUPP` are normal. Some methods can be intentionally expensive and dominate runtime. Non-`crypt_r()` builds use process-global `crypt()` state, which is less thread-safe in general, although stress-ng workers are process-based. The single-method branch uses the selected index; option parsing must keep it in range.

## Test Signals
Builds without libcrypt should register the unimplemented reason. Runtime signals include successful metrics for available methods, graceful silence for unavailable methods, bogo increments on successful encryptions, and no fatal failure for expected unsupported-algorithm errors. Testing should cover both all-method and selected-method modes.
