# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_network.rs

Purpose: emits internode network metrics for RustFS cluster communication: failed internode calls, dial errors, average dial time, sent bytes, and received bytes.

Important APIs/types: `NetworkStats` and `collect_network_metrics`.

Control flow: fixed five-metric vector with no labels. All fields are direct conversions from the DTO.

State/persistence: no local state. Upstream `collect_internode_network_stats` provides optional snapshots.

Dependencies/integration: scheduler runs an internode/system network task at `system_interval`; if optional stats exist and metrics are non-empty, it reports them.

Risks: average dial time is in nanoseconds while other values are counts/bytes, so descriptor units matter. Unlabeled aggregate output cannot distinguish peers or endpoints; detailed peer metrics would require a separate collector.

Test signals: tests assert five metrics, all names containing `internode`, `report_metrics` compatibility, and default zero/no-label behavior.
