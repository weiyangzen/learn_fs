# sources/object-store/rustfs/crates/protocols/src/sftp/lifecycle.rs

## Purpose
`lifecycle.rs` holds the per-session diagnostic record, weak live-session registry, and Linux TCP-state probe used by the SFTP wedge watchdog.

## Important APIs, Types, and Functions
`SessionDiag` stores `session_id`, local and peer addresses, `accepted_at`, and relaxed atomic `last_activity_ms`; `new` initializes it and `stamp` refreshes activity. `SessionRegistry` is a `Mutex<Vec<Weak<SessionDiag>>>`. `TcpState` normalizes Linux procfs state bytes into `Established`, `CloseWait`, or `Other(u8)`. `probe_tcp_state` reads `/proc/net/tcp` and `/proc/net/tcp6`, `lookup_tcp_state` matches rows, and `render_proc_net_tcp_addr` renders IPv4/IPv6 socket tuples in procfs format.

## Control Flow
The accept loop creates a `SessionDiag`, registers a weak ref, and shares strong refs with the SSH handler, SFTP driver, and watchdog. Handlers stamp activity. On Linux, the watchdog probes procfs, first IPv4 then IPv6, matching local/remote address-port columns and parsing the state byte.

## State and Persistence Behavior
All state is in memory. The registry uses weak refs so it does not extend sessions. `last_activity_ms` is relaxed because it is a best-effort liveness signal, not a synchronization primitive.

## Dependencies and Integration Points
The file uses standard networking, synchronization, procfs reads, and formatting. `server.rs` owns session construction and registry insertion. `wedge_watchdog.rs` consumes the TCP probe; `fallback_watchdog.rs` consumes only activity stamps.

## Risks and Test Signals
Risks include procfs format drift, byte-order mistakes, stale weak entries, and false negatives when procfs is unavailable. Tests cover IPv4, IPv4-mapped IPv6, native IPv6 rendering, unsupported native IPv6 in the IPv4 table, close-wait/established lookup, no-match behavior, and `Other` state parsing.
