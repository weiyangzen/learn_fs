# sources/object-store/rustfs/crates/utils/src/ip.rs

## Purpose
Provides simple local-machine IP discovery helpers with a loopback fallback.

## Important APIs, Types, And Functions
`get_local_ip` attempts `local_ip_address::local_ip()` first and then `local_ip_address::local_ipv6()`, returning `Option<IpAddr>`. `get_local_ip_with_default` converts the result to a string and falls back to `127.0.0.1`.

## Control Flow And State
No persistent state is kept. Each call queries the `local_ip_address` crate. Fallback behavior is deterministic only when no address is found.

## Dependencies And Integration Points
Uses `std::net::{IpAddr, Ipv4Addr}` and the `local_ip_address` crate. It is exposed from `lib.rs` under the `ip` feature and is a smaller counterpart to the richer `net.rs` local-interface helpers.

## Risks And Test Signals
Tests assume the host can discover at least one local IP and that repeated calls are stable; those are environment-sensitive in containers, CI, or systems with dynamic interfaces. Functional risk is low, but the selected IP may not match the desired bind or advertise address on multi-homed hosts.
