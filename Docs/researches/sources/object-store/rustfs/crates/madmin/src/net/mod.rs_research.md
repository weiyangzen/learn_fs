# sources/object-store/rustfs/crates/madmin/src/net/mod.rs

Purpose: provides the admin network information shape and a platform-gated `get_net_info` constructor.

Important APIs/types/functions: `get_net_info(addr, iface) -> NetInfo` fills common node address and interface name. On Linux it returns a default `NetInfo` with address/interface only. On non-Linux it returns `NetInfo` with `NodeCommon.error` set to a not-implemented message. `NetInfo` contains `node_common`, `interface`, `driver`, and `firmware_version`.

Control flow: compile-time `cfg(target_os = "linux")` selects the implementation. There is no probing of driver, firmware, ethtool, or OS network state yet.

State and persistence: no persistence. Returned values are request-local snapshots; most fields remain default-empty.

Dependencies/integration: depends on serde and `health::NodeCommon`. It is exposed as `madmin::net`, but not glob re-exported by `lib.rs`.

Risks: `NetInfo` fields are private, which is fine for serde output from inside the crate but restricts downstream construction/inspection unless accessor APIs are added. Linux implementation can look complete while omitting driver/firmware/error data. Non-Linux callers get an error string but still receive the requested interface.

Test signals: no local tests. Current behavior is compile-time validated only; future platform probing should add Linux and non-Linux unit or integration tests around populated fields and error semantics.
