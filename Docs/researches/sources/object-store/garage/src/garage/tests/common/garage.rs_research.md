# sources/object-store/garage/src/garage/tests/common/garage.rs

Purpose: This file owns the real Garage process used by integration tests. It creates a temporary config/runtime directory, starts the binary, waits for boot, configures single-node layout, creates test keys, exposes endpoint URIs, and terminates the process at test shutdown.

Important APIs and types: `DEFAULT_PORT`, `GARAGE_TEST_SECRET`, `Key`, `Instance`, `instance`, and `command` are central. `Instance` stores the child process, runtime path, default key, S3/K2V/Web/Admin ports, and helper methods `setup`, `wait_for_boot`, `setup_layout`, `terminate`, `node_id`, `s3_uri`, `k2v_uri`, and `key`.

Control flow: `Instance::new` chooses a port/path/db engine from environment or defaults, deletes and recreates the runtime directory, writes a full config file, opens stdout/stderr logs, and spawns `garage server`. `setup` polls `garage status`, assigns/apply layout for one node, and creates a default key via `json-api CreateKey`. A global `OnceLock` initializes one instance lazily, and a `static_init` destructor kills the child process.

State and persistence behavior: Persistent test state lives under the runtime directory: config, metadata, data, stdout, and stderr. The server process persists cluster layout, keys, buckets, and objects there for the duration of the integration run. The harness aggressively removes any previous directory for the selected port.

Dependencies and integration points: It depends on `serde_json`, the Garage binary path from `GARAGE_TEST_INTEGRATION_EXE` or `CARGO_BIN_EXE_garage`, process helpers, and CLI commands. It is the root integration point for all tests in `garage/tests`.

Risks: The destructor uses `kill` rather than graceful SIGTERM. Port allocation is fixed by default and can conflict with other runs. `wait_for_boot` loops for up to two minutes but does not explicitly fail if status never succeeds before layout commands run. Removing the runtime path can delete user-provided `GARAGE_TEST_INTEGRATION_PATH` content if misconfigured.

Test signals: Every integration test's ability to create buckets, sign requests, and talk to S3/K2V/Web/Admin confirms that this harness successfully bootstrapped a usable single-node Garage cluster.
