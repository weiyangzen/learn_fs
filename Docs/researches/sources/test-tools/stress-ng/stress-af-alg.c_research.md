# sources/test-tools/stress-ng/stress-af-alg.c

## Purpose
`stress-af-alg.c` implements the `af-alg` stressor for Linux kernel crypto sockets, exercising hash, cipher/skcipher, AEAD, and RNG algorithms discovered from `/proc/crypto` plus built-in default configurations.

## Important APIs, Types, And Functions
The stressor uses `stress_crypto_type_t`, `stress_crypto_info_t`, and a linked `crypto_info_list`. Option handlers expose `--af-alg-dump` and `--af-alg-type`. Work functions include `stress_af_alg_hash`, `stress_af_alg_cipher`, `stress_af_alg_aead`, and `stress_af_alg_rng`. Discovery and list management include `name_to_type`, `type_to_type_string`, `stress_af_alg_count_crypto`, `stress_af_alg_sort_crypto`, `stress_af_alg_dump_crypto_list`, `dup_field`, `int_field`, `bool_field`, `stress_af_alg_add_crypto`, `stress_af_alg_add_crypto_defconfigs`, `stress_af_alg_init`, `stress_af_alg_deinit`, and `stress_af_alg_info_free`.

## Control Flow
Initialization parses `/proc/crypto` into crypto-info records, merges static defconfigs, sorts and optionally dumps the list. The stressor selects algorithms matching the requested type, opens AF_ALG sockets, binds by type/name, sets keys or auth sizes where needed, accepts operation sockets, sends random input through `send`, `sendmsg`, or reads RNG output, validates decrypt round-trips for ciphers, records per-algorithm metrics, and increments bogo ops. An alarm handler can longjmp out if an AF_ALG operation wedges after stop is requested.

## State And Persistence
Runtime state is the heap-owned crypto list, per-entry ignore/selftest flags and metrics, AF_ALG sockets, random buffers, signal jump state, and stress-ng bogo counters. It reads `/proc/crypto` and may trigger kernel module autoloading through bind. It does not write files.

## Dependencies And Integration Points
It requires Linux `AF_ALG`, `linux/if_alg.h`, `linux/socket.h`, socket APIs, crypto procfs format, random buffer helpers, sorting, metrics, and stress-ng signal handling. It is registered as `CLASS_CPU | CLASS_OS` with optional verification; unsupported builds expose `stress_unimplemented`.

## Risks
Kernel crypto providers vary widely; many bind, key, IV, auth-size, and selftest failures must be treated as skip/ignore rather than stressor failure. AF_ALG operations can hang or return surprising errno values, so alarm/longjmp cleanup is critical. Size fields are stored in small signed integer types, making catalog accuracy important.

## Test Signals
`--af-alg`, `--af-alg-type`, and `--af-alg-dump` are direct tests. Debian lite tests include `af-alg`; kernel coverage exercises it more heavily. Useful signals include successful algorithm count, skipped unsupported engines, no stuck sockets after SIGALRM, and nonzero per-algorithm operation metrics.
