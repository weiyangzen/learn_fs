# File Research: sources/virtualization/spdk/lib/accel/accel_rpc.c

`accel_rpc.c` implements JSON-RPC control-plane methods for the accel framework. It is runtime/startup glue over the core APIs in `accel.c` and the internal helpers from `accel_internal.h`.

Registered RPCs include `accel_get_opc_assignments`, `accel_get_module_info`, `accel_assign_opc`, `accel_crypto_key_create`, `accel_crypto_keys_get`, `accel_crypto_key_destroy`, `accel_set_driver`, `accel_set_options`, and `accel_get_stats`.

Opcode assignment RPCs translate between opcode strings and enum values, validate requested operation names, and call `spdk_accel_assign_opc()`. Assignment is startup-only, matching the framework restriction that opcode-to-module overrides must be set before modules start.

Crypto-key RPCs decode cipher, key, optional key2, optional tweak mode, and key name. They translate decoded enum values back to framework strings and call `spdk_accel_crypto_key_create()`. Sensitive key strings decoded from RPC are explicitly scrubbed with `spdk_memset_s()` before freeing. Key listing can dump one key by name or all keys; destruction resolves the key object then calls the framework destroy routine.

Driver and option RPCs call `spdk_accel_set_driver()` and `spdk_accel_set_opts()`. Option decoding avoids direct packed-struct decode by copying into an RPC-specific context first, then back into `spdk_accel_opts`.

Stats RPC aggregation is asynchronous. `accel_get_stats()` supplies an `accel_stats` snapshot, and the RPC writer emits sequence counters, outstanding task counters, retry counters, and only operation entries that have executed or failed counts. Each operation entry includes opcode name, assigned module name, executed, failed, and byte totals.

Research notes: error responses use SPDK JSON-RPC error codes for parse/invalid-param failures and `spdk_strerror()` for framework return codes. The file is strictly control plane; no datapath operations are issued here.
