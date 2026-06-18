# sources/object-store/rustfs/crates/madmin/src/service_commands.rs

Purpose: parses service trace query options into a trace bitmask and threshold settings for admin/service trace commands.

Important APIs/types/functions: `ServiceTraceOpts` stores booleans for S3, internal, storage, OS, scanner, decommission, healing, batch replication/key rotation/expire/all, rebalance, replication resync, bootstrap, FTP, ILM, error-only filtering, and a `Duration` threshold. `trace_types` builds a `TraceType` mask. `parse_params(&Uri)` reads query parameters and parses `threshold` via `utils::parse_duration`.

Control flow: `parse_params` splits the URI query on `&` and `=`, defaults missing values to `"false"`, sets booleans only when value is exactly `"true"`, expands `all=true` to S3/internal/storage/OS, and parses optional threshold. `trace_types` handles `batch_all` by enabling all batch trace bits.

State and persistence: state is in the mutable options struct for one parsed request. No persistence.

Dependencies/integration: depends on `hyper::Uri`, `trace::TraceType`, and `utils::parse_duration`/`humantime`. It bridges HTTP query strings to trace filtering.

Risks: query parsing is ad hoc: it does not percent-decode, ignores repeated keys except the last via `HashMap`, and loses values containing `=`. `batch_all` is not populated by `parse_params`, so only direct struct construction can currently trigger all batch trace bits. `only_errors` is parsed but not used in `trace_types`.

Test signals: no local tests. Duration parsing is covered in `utils.rs`; trace option parsing needs focused tests for `all`, threshold errors, repeated keys, and batch flags.
