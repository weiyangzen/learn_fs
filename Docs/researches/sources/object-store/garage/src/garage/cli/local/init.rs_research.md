# sources/object-store/garage/src/garage/cli/local/init.rs

Purpose: prints this node's Garage RPC node identifier and helpful connection/bootstrap instructions.

Important APIs/types/functions: constant `READ_KEY_ERROR` and `node_id_command(config_file, quiet)`.

Control flow: reads config, reads node ID from metadata directory, prints `node_id@public_addr` if `rpc_public_addr` is set, otherwise prints raw ID and warns/instructs using `127.0.0.1:<rpc_bind_port>` as a placeholder when not quiet. Non-quiet mode prints connection command, bootstrap config snippet, and security notice.

State and persistence: reads config file and node key from metadata; does not modify state.

Dependencies and integration points: uses `garage_util::config::read_config`, `garage_rpc::system::read_node_id`, `hex`, and tracing warnings. Used by local initialization/operator CLI flows.

Risks: output with fallback loopback address is intentionally instructional and may be copied incorrectly if user ignores warning. Failure to read node key is normal before first node launch and surfaced with a long contextual message.

Test signals: no unit tests; manual CLI invocation is the main check.
