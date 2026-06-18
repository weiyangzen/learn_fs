# sources/object-store/garage/src/rpc/Cargo.toml

Purpose: crate manifest for `garage_rpc`, the Garage cluster membership and RPC support crate.

Important configuration: the package is version `2.3.0`, edition 2018, AGPL-3.0, with `lib.rs` as the crate root. The description identifies it as "Cluster membership management and RPC protocol for the Garage object store".

Dependencies: internal workspace crates are `garage_util` and `garage_net`; external workspace dependencies include `arc-swap`, `bytesize`, `gethostname`, `hex`, `ipnet`, `tracing`, `rand`, `itertools`, `sodiumoxide`, `nix`, `async-trait`, `serde`, `serde_bytes`, `serde_json`, `utoipa`, `pnet_datalink`, `futures`, `tokio`, and `opentelemetry`. Optional dependencies support discovery: `reqwest` and `thiserror` for Consul, `kube`, `k8s-openapi`, and `schemars` for Kubernetes.

Features and integration: `kubernetes-discovery` enables Kubernetes CRD/client dependencies; `consul-discovery` enables HTTP/TLS Consul discovery; `system-libs` forwards `sodiumoxide/use-pkg-config`. Workspace lints are inherited.

State and persistence behavior: no runtime state itself, but the selected features control whether `system.rs` can advertise/discover peers via Consul or Kubernetes.

Risks and test signals: feature combinations must stay aligned with conditional modules in `lib.rs` and `system.rs`. The manifest note says newer `kube` requires Rust 2021, so dependency upgrades can be constrained by the crate's edition/toolchain support. Optional dependency drift can break discovery builds while core RPC still compiles.
