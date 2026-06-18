# File Research: sources/virtualization/spdk/lib/init/json_config.c

`json_config.c` loads SPDK JSON configuration by replaying configured JSON-RPC methods against a temporary in-process RPC server. It parses the `"subsystems"` array, walks subsystem config entries, filters methods by RPC state, sends requests over a temporary Unix-domain JSON-RPC client/server pair, and optionally advances subsystem initialization between startup and runtime phases.

The expected JSON shape is a root object with `"subsystems"` entries, each containing a subsystem name and a `"config"` array. Config entries can be individual RPC objects with `"method"` and optional `"params"`, or explicit arrays that are sent as JSON-RPC batch requests.

`load_json_config_ctx` owns the parsed JSON buffer/token array, current subsystem/config iterators, current method request ID, stop-on-error behavior, temp RPC socket path, JSON-RPC client connection, poller, active response handler, timeout, and a flag controlling whether subsystem initialization should be performed.

The loader copies and parses JSON with comment support, locates the `"subsystems"` array, starts a temporary RPC server with a unique socket name derived from `SPDK_DEFAULT_RPC_ADDR`, pid, and ticks, connects a JSON-RPC client, and drives connection/request progress through SPDK pollers on the app thread.

Individual requests preserve raw `"params"` JSON rather than decoding it locally. Method state masks from `spdk_rpc_get_method_state_mask()` determine whether a method should run in STARTUP or RUNTIME. Methods allowed in both states are skipped during the second runtime pass to avoid duplicate execution. Missing methods can be skipped when the referenced subsystem is not linked into the application, supporting reuse of config files across SPDK apps with different linked subsystems.

Batch handling builds one JSON-RPC batch request from an explicit config array, computes the intersection of allowed state masks for all batch elements, skips batches not applicable to the current state, and rejects batches whose methods have incompatible state requirements. Empty or invalid batches are treated as errors.

When subsystem initialization is enabled, the first pass runs STARTUP methods. After all entries are walked in STARTUP state, it calls `spdk_subsystem_init()`, switches RPC state to RUNTIME in the init callback, then walks the config again for runtime methods. `spdk_subsystem_load_config()` uses the same machinery without initializing subsystems.

Timeout handling intentionally warns every 10 seconds for outstanding RPC requests rather than failing them, because SPDK RPC commands generally do not have hard timeouts. Connection setup has a shorter 1 second timeout.

Research notes: the file’s important behavior is the state-aware two-pass replay model and the temporary RPC-loopback design. The code relies on app-thread execution, async pollers, raw JSON forwarding, and careful cleanup of poller/client/server resources in `app_json_config_load_done()`.
