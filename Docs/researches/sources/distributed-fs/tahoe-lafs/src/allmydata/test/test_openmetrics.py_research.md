# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_openmetrics.py

## Purpose
Tests the `/statistics?t=openmetrics` endpoint for OpenMetrics-compatible status, content type, UTF-8 body, parser compatibility, and expected Tahoe metric output.

## APIs / Types / Functions
- `FakeStatsProvider.get_stats` returns canned real-world-like Tahoe stats and counters.
- `HackItResource` adapts `RequestTraversalAgent` requests for `MultiFormatResource`.
- `OpenMetrics.test_spec_compliance` mounts `Statistics(FakeStatsProvider())`.
- Matchers `matches_stats`, `has_header`, `readBodyText`, and `parses_as_openmetrics` validate the response.

## Control Flow
The test builds an in-memory Twisted resource tree, requests `/?t=openmetrics`, asserts HTTP 200 and exact OpenMetrics content type, decodes the response, records body detail, parses it with `prometheus_client.openmetrics.parser`, and checks the last metric family name is `tahoe_stats_storage_server_total_bucket_count`.

## State And Persistence
All stats are in-memory dictionaries. No sockets or files are used.

## Dependencies / Integration Points
Integrates Tahoe web status `Statistics`, Twisted Web, `treq.testing.RequestTraversalAgent`, testtools matchers, and Prometheus/OpenMetrics parser behavior.

## Risks And Test Signals
The last-family assertion encodes deterministic grouping/sorting beyond simple spec compliance. It does not validate every metric value. Passing tests show parseable OpenMetrics output with correct media type and expected storage metrics.
