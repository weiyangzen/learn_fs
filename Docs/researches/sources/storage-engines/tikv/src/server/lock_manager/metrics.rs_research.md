# sources/storage-engines/tikv/src/server/lock_manager/metrics.rs

Purpose: declares Prometheus metrics for lock-manager tasks, errors, wait lifetimes, detection latency, detector leadership, and wait-table gauges.

Important APIs/types/functions: static metric families include `LocalTaskCounter`, `LocalErrorCounter`, `WaitTableStatusGauge`, `TASK_COUNTER_VEC`, `ERROR_COUNTER_VEC`, `WAITER_LIFETIME_HISTOGRAM`, `DETECT_DURATION_HISTOGRAM`, `DETECTOR_LEADER_GAUGE`, and auto-flushing local handles.

Control flow: there is no runtime control flow beyond lazy registration. Other lock-manager modules increment task/error counters, observe lifetimes and detect duration, and set the leader gauge during role changes.

State and persistence: metrics live in Prometheus registry/global statics and local auto-flush counters. They are process metrics only.

Dependencies and integration: uses `lazy_static`, `prometheus`, and `prometheus_static_metric`. Integrated throughout `deadlock.rs` and `waiter_manager.rs`.

Risks: label sets are fixed at compile time; adding task/error categories requires updating static metric definitions. Metrics registration unwraps and will panic on duplicate registration, as expected for TiKV metric statics.

Test signals: no direct tests; metrics are exercised by lock-manager unit tests that increment counters and observe histograms.
