# sources/storage-engines/wiredtiger/test/catch2/ext/test_key_provider.cpp

## Purpose
Exercises the test key-provider extension and WiredTiger disaggregated-storage key-provider integration. The file covers extension initialization/configuration, pull-mode key rotation, push-mode `WT_KEY_PROVIDER::set_key`, pending crypt-key queue ordering, checkpoint key selection/pruning, and full pending-key cleanup.

## Important APIs, Types, And Functions
`kp_fixture` owns a `connection_wrapper`, `WT_SESSION`, extension init pointer, and raw `KEY_PROVIDER`. `kp_init` calls `wiredtiger_extension_init` or the built-in extension initializer, then reads `WT_CONNECTION_IMPL::key_provider`. `kp_reset` terminates the provider and clears the connection field. `kp_load_key`, `kp_get_key`, and `push_key` wrap `load_key`, two-phase `get_key`, `on_key_update`, and push-mode `set_key`. `validate_chosen_key` and `validate_pending_queue` inspect `WT_DISAGG_PENDING_CRYPT_KEY` entries. The tests call `WT_CONNECTION::set_key_provider`, `WT_CONNECTION::set_timestamp`, `__ut_disagg_select_pending_crypt_key`, `__ut_disagg_prune_pending_crypt_keys`, and `__wti_disagg_pending_crypt_key_clear`.

## Control Flow
The fixture opens an in-memory WiredTiger database and session, initializes the extension on demand, and tears it down in RAII style. Early sections validate null, empty, custom, and invalid config. Pull-mode sections force expiration by moving `key_time`, then verify `get_key` transitions `CURRENT -> PENDING -> READ` and `on_key_update` either commits the new LSN/state or leaves a failed read pending. Push-mode sections configure `version=1`, push key bytes with timestamps, assert monotonic and stable-timestamp constraints, then exercise checkpoint selection and pruning over the pending queue.

## State And Persistence Behavior
The tests directly inspect volatile connection state: provider fields, `WT_CONN_KEY_PROVIDER_PUSH`, `KEY_STATE_*`, current key bytes, LSN, key age, and the disaggregated pending crypt-key tail queue. They simulate persistence boundaries by invoking checkpoint selection/prune helpers, but do not write real disaggregated checkpoint metadata. Queue cleanup is explicit to avoid fixture destruction seeing stale entries.

## Dependencies And Integration Points
Depends on Catch2, `ext/test/key_provider/key_provider.h`, `connection_wrapper`, `utils::shared_library`, `wiredtiger.h`, and `wt_internal.h`. It integrates extension ABI behavior with core connection configuration, disaggregated-storage timestamp checks, and checkpoint crypt-key selection helpers.

## Risks And Edge Cases
Risks are stale raw provider pointers, manual clearing of `conn_impl->key_provider`, memory returned by `get_key` that must be freed, and direct mutation of internals that can hide lifecycle errors if cleanup is missed. The test intentionally covers invalid config strings, one-shot expiration semantics, queueing failures, non-monotonic timestamps, stable-timestamp rejection, empty push input, selection before the first key, and pruning an empty or fully covered queue.

## Test Signals
Catch2 assertions validate every state transition and queue shape. Failure signals include `EINVAL` for bad config or invalid push timestamps, unchanged LSN on queueing failure, exact queue order after pushes/prunes, and selected key timestamp/bytes for checkpoint timestamps.
