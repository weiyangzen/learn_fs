# sources/storage-engines/wiredtiger/ext/test/key_provider/key_provider.c

## Purpose
This file implements a mock `WT_KEY_PROVIDER` extension for testing encryption key management, including key loading, pull-mode key rotation, push-mode key update confirmation, expiration, and registration.

## Important APIs, Types, and Functions
The central object is `KEY_PROVIDER`, cast to `WT_KEY_PROVIDER`. The vtable is filled with `kp_load_key`, `kp_get_key`, `kp_on_key_update`, and `kp_terminate`. `key_provider_extension_init` is the common initializer; `wiredtiger_extension_init` wraps it for module builds unless builtin mode is configured. Helpers include `kp_set_key`, `kp_free_key`, `kp_timestamp`, `kp_key_expired`, `kp_generate_key`, `kp_rotate_key`, `kp_configure`, and `configure_int`.

## Control Flow
Initialization allocates the provider, sets defaults, installs the default key, parses `version`, `verbose`, and `key_expires`, installs the vtable, calls `WT_CONNECTION->set_key_provider`, and marks the first key for one-shot expiration. In pull mode, `kp_get_key` first reports size for an expired generated key, then fills a caller buffer, and `kp_on_key_update` confirms the LSN. `kp_load_key` loads persisted checkpoint key material. In push mode, `on_key_update` accepts a confirmed key and enforces increasing timestamp and LSN.

## State and Persistence Behavior
The provider stores key bytes, size, LSN, timestamp, state-machine state, and key creation time in memory. It does not persist keys itself; WiredTiger persists and reloads key material through `WT_CRYPT_KEYS`. Generated keys combine a default prefix and ISO8601 timestamp pattern with randomized size near 1024 bytes.

## Dependencies and Integration Points
The file depends on `wiredtiger_ext.h`, the `WT_KEY_PROVIDER` interface, C allocation/string/time APIs, and Windows `FILETIME` support. It integrates with checkpoint encryption through `set_key_provider`, `WT_CRYPT_KEYS`, and update callbacks.

## Risks and Edge Cases
Assertions enforce state ordering, key-size matches, and monotonic push-mode values. `clock()` measures CPU time on non-Windows systems. `localtime` and `rand` are test-grade choices. The provider has no explicit locking and relies on callback serialization.

## Test Signals
Tests should cover one-shot expiration, unchanged-key responses, pull-mode size/data/update sequence, failed update, persisted-key load, push-mode monotonic checks, config errors, and termination cleanup.
