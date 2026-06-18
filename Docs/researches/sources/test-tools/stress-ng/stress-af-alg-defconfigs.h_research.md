# sources/test-tools/stress-ng/stress-af-alg-defconfigs.h

## Purpose
`stress-af-alg-defconfigs.h` provides a static catalog of Linux crypto algorithm configurations for the AF_ALG stressor to try even when modules are not yet listed in `/proc/crypto`.

## Important APIs, Types, And Functions
The file is an initializer fragment for `stress_crypto_info_t crypto_info_defconfigs[]`. Entries set fields such as `.crypto_type`, `.type`, `.name`, `.block_size`, `.max_key_size`, `.max_auth_size`, `.iv_size`, and `.digest_size` for AEAD, AHASH, AKCIPHER, CIPHER, RNG, SHASH, and SKCIPHER algorithms.

## Control Flow
It has no standalone control flow. `stress-af-alg.c` includes it inside an array initializer, then copies entries into the runtime crypto list via `stress_af_alg_add_crypto_defconfigs`.

## State And Persistence
The catalog is read-only compiled data. At runtime, entries are duplicated into heap-owned `stress_crypto_info_t` nodes with source `SOURCE_DEFCONFIG`.

## Dependencies And Integration Points
It depends on enum values and structure fields defined in `stress-af-alg.c`, so it is not a self-contained header. It integrates with AF_ALG bind attempts that can autoload crypto modules.

## Risks
Incorrect key, IV, digest, block, or auth sizes can cause false AF_ALG failures or skipped algorithms. Kernel crypto algorithm names change over time, and unsupported algorithms should be ignored cleanly. Because the file is included as an initializer, syntax errors break the parent C file.

## Test Signals
`--af-alg` and `--af-alg-dump` show whether defconfig entries are merged and exercised. Kernel coverage and lite autopkgtest include `af-alg`, providing broad smoke coverage on Linux systems with AF_ALG.
