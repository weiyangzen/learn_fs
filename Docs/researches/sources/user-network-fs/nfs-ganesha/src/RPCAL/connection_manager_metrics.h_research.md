# sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager_metrics.h

Purpose: declares the metric handle container and update API used by the connection manager.

Important APIs and types: `connection_manager__metrics_t`, `gauge_metric_handle_t clients[]`, `histogram_metric_handle_t connection_started_latencies[]`, `histogram_metric_handle_t drain_local_client_latencies[]`, plus declarations for init, gauge increment/decrement, and histogram completion functions.

Control flow: no implementation control flow. Array dimensions are tied to `CONNECTION_MANAGER__CLIENT_STATE__LAST`, `CONNECTION_MANAGER__CONNECTION_STARTED__LAST`, and `CONNECTION_MANAGER__DRAIN__LAST`.

State and persistence: describes in-memory metric handles managed by `connection_manager_metrics.c` and the monitoring subsystem.

Dependencies and integration points: includes `connection_manager.h` for enums and `monitoring.h` for handle types. This header is consumed by `connection_manager.c` and metrics implementation.

Risks: no include guard is visible in this header, so repeated inclusion depends on current include patterns not causing duplicate typedef issues. Enum count changes require corresponding stringify support and registration loops in the `.c` file.

Test signals: compile all translation units including this header, run builds with strict warnings, and verify enum additions fail review unless metrics registration and labels are updated.
