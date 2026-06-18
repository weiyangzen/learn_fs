<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/adaptive_ttl.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/adaptive_ttl.rs

### Purpose
Provides metric helpers for adaptive TTL behavior plus in-memory access-frequency tracking used by cache TTL decisions.

### Important APIs, Types, And Functions
Recording functions emit TTL adjustment, expiration, early eviction, and access-pattern-change metrics. `AdaptiveTTLStats` is a plain counter summary with adjustment/extension/reduction/expiration/eviction counts and rate helpers. `AccessRecord` tracks count, first/last access, total size, frequency, and idle time. `AccessTracker` maintains a bounded `HashMap<String, AccessRecord>` and exposes `record_access`, count/record lookups, hot/cold checks, `top_keys`, `prune`, `len`, `is_empty`, `clear`, totals, and averages.

### Control Flow
Metric functions call `metrics` macros directly. `AccessTracker::record_access` updates existing records or evicts the oldest record when the map reaches `max_items`, then inserts a new record. `prune` removes records whose last access is outside the configured window. `top_keys` sorts by count descending.

### State And Persistence
`AdaptiveTTLStats` and `AccessTracker` are in-memory only. `AccessTracker` records are local to one tracker instance and are not synchronized internally; callers must provide synchronization if shared across threads.

### Dependencies And Integration Points
Uses `metrics`, `HashMap`, and `Instant`. Integrates with `cache_config::AdaptiveTTL` by providing the access counts and pattern telemetry that TTL decisions can consume.

### Risks
Metric labels `reason`, `from`, and `to` are dynamic strings; unbounded caller-provided values can increase cardinality. `AccessRecord::new` starts count at 1, and `record_access` then increments on existing records, so semantics assume insertion itself is an access. Frequency is computed since first access over the entire record lifetime, not over the configured window unless old records are pruned.

### Test Signals
Tests cover stats rates, metric helper execution, access-record mutation, tracker insertion/update/totals, hot/cold checks, top-key ordering, and clear behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/adaptive_ttl.rs -->
