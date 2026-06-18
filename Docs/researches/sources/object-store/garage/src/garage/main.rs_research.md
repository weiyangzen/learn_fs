# sources/object-store/garage/src/garage/main.rs

Purpose: This is the `garage` binary entrypoint. It initializes build/version metadata, installs a panic-aborting hook, parses CLI arguments, configures logging, initializes sodiumoxide, creates a Tokio runtime, and dispatches server, local, schema, completion, and remote admin commands.

Important APIs and types: `Opt` combines `rpc_host`, flattened `Secrets`, `config_file`, and `Command`. `main`, `run`, `init_logging`, and `cli_command` are the key functions. Remote command setup uses `NetworkKey`, `NetApp`, `parse_and_resolve_peer_addr`, `AdminRpc`/`ADMIN_RPC_PATH`, local node ID reading, and `cli::remote::Cli`.

Control flow: `main` validates compile-time feature combinations, initializes version/features, sets a panic hook that prints version and backtrace before aborting, then parses clap matches with the computed version string. `run` dispatches server/offline repair/convert-db/node-id/schema/completion locally and sends all other commands through `cli_command`. `cli_command` reads config only when RPC host or secret is missing, resolves and validates the RPC secret, builds a temporary signing keypair, connects to the target node, creates an admin proxy endpoint, and calls the remote CLI handler.

State and persistence behavior: Persistent state is read from the config file, metadata directory node ID, and optional secret files. Runtime state includes environment variables for logging defaults, the global tracing subscriber, a sodiumoxide initialization, and a transient NetApp client. The panic hook deliberately aborts the process to avoid continuing after a Tokio task panic.

Dependencies and integration points: It integrates `structopt`, `tracing_subscriber`, optional syslog/journald logging, `garage_rpc`, `garage_net`, admin API RPC proxying, OpenAPI generation, local CLI modules, and secret loading from `secrets.rs`. It is also the test harness binary invoked by integration tests through `CARGO_BIN_EXE_garage`.

Risks: Logging setup mutates `RUST_LOG` before runtime construction and exits if requested syslog/journald support is absent at compile time. RPC host fallback uses local config and may warn on default localhost failure. Secret validation is strict on hex and key length. The abort-on-panic policy is operationally safe but can make tests or development runs fail hard.

Test signals: The integration harness depends on this path for starting the server, running `status`, `node id`, `layout`, `bucket`, `key`, and `json-api`. Secret-specific unit tests live in `secrets.rs`; remote command connectivity is implicitly tested by every CLI-backed integration setup step.
