# sources/object-store/openstack-swift/swift/common/statsd_client.py

## Purpose

This module is Swift's UDP StatsD emission layer. It builds legacy metric names, supports optional labeled metrics in several collector dialects, applies sampling, and isolates metric-send failures from service request handling. It is used by loggers and service code that need counters, timings, and transfer-rate metrics without taking a dependency on a long-lived StatsD socket.

## Important APIs, types, and functions

`get_statsd_client(conf, tail_prefix, logger)` reads `log_statsd_host`, `log_statsd_port`, `log_statsd_default_sample_rate`, `log_statsd_sample_rate_factor`, `log_statsd_metric_prefix`, and `statsd_emit_legacy`, returning a `StatsdClient`. `get_labeled_statsd_client(conf, logger)` reads the same host/port/sample settings plus `statsd_label_mode` and user labels whose config keys start with `statsd_user_label_`.

Formatting helpers include `_build_line_parts()` and dialect functions `librato()`, `influxdb()`, `graphite()`, and `dogstatsd()`. `LABEL_MODES` maps mode names to formatter callables, while `_get_labeled_statsd_formatter()` validates the configured mode.

`AbstractStatsdClient` owns host/port configuration, DNS-family detection, sampling, socket creation, send error handling, and common metric methods. `_is_emitted()` applies default sample rate and sample-rate factor and uses an injectable `random` function for tests. `_send_line()` opens a UDP socket for each datagram, sends UTF-8 bytes, and logs warnings without propagating send errors.

`StatsdClient` implements legacy unlabeled metrics with optional `base_prefix` and `tail_prefix`. It preserves older positional `sample_rate` arguments on `update_stats()`, `increment()`, `decrement()`, `timing()`, `timing_since()`, and `transfer_rate()`. `LabeledStatsdClient` emits labeled lines with keyword-only `labels` and `sample_rate`, merges caller labels with configured default labels, sorts labels for deterministic output, and disables output when `statsd_label_mode` is `disabled`.

## Control flow

Client construction resolves the target socket family by trying IPv4 and then IPv6 `getaddrinfo()`. If both fail, startup continues with an IPv4 family and the original host, allowing later `sendto()` name resolution to succeed. A metric method funnels through `_send()`, then `_is_emitted()`, then line formatting, then `_send_line()`. Sampling short-circuits before formatting when the adjusted sample rate is below a random draw. `transfer_rate()` emits only when `byte_xfer` is non-zero, calculating milliseconds per kilobyte-like unit from elapsed time and transferred bytes.

For labeled clients, default user labels are validated at configuration load time: label names allow only ASCII alphanumerics and underscore, and label values additionally allow periods. The configured names are prefixed with `user_` to avoid collisions with internal label namespaces.

## State and persistence behavior

The clients hold only in-memory configuration and do not persist metrics. They intentionally do not cache sockets because a shared socket would be unsafe across Swift green threads. `_target` preserves the configured host instead of pinning a resolved address, so DNS changes can take effect through normal resolver behavior. `StatsdClient.set_prefix()` mutates the legacy metric prefix and emits a deprecation warning.

## Dependencies and integration points

The module imports `socket` from `swift.common.concurrency`, so the socket implementation follows Swift's eventlet/concurrency abstraction. It uses `config_true_value()` for boolean config parsing. The clients are typically constructed by Swift logger setup and passed into service components; metric methods are deliberately narrow enough to be used from hot request paths.

StatsD label syntax is collector-specific. Librato appends `#k=v`, InfluxDB appends `,k=v` to the measurement name, Graphite appends `;k=v`, and DogStatsD appends `|#k:v` after the base StatsD line.

## Risks and edge cases

There is no explicit validation that sample rates are between 0 and 1. Values above 1 omit the `|@` suffix and always emit; negative values effectively never emit but have surprising semantics. UDP send failures are logged and swallowed, which is operationally appropriate but means metric loss is silent unless warnings are observed. Opening a socket per metric avoids green-thread sharing but adds overhead in high-volume paths.

Labeled and legacy clients intentionally expose different call signatures: legacy accepts positional `sample_rate`, while labeled uses keyword-only labels and sample rate. Callers migrating between them need tests. Label validation covers configured user labels but not per-call labels, so caller-provided labels can still contain dialect-breaking characters or high-cardinality values.

## Test signals

Strong tests include formatter output for each label mode, invalid label-mode errors, user-label validation failures, prefix construction, sampling boundaries with a deterministic `random`, disabled host behavior, DNS fallback behavior, UDP send error logging, deprecated `set_prefix()` warnings, and compatibility of legacy positional `sample_rate`. Labeled-client tests should verify deterministic label sorting and default-label override behavior.
