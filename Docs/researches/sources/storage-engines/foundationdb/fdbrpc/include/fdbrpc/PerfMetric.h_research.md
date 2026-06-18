## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/PerfMetric.h

Purpose: Defines simple serializable performance metric values and lightweight integer/double counters that emit those metrics.

Important APIs/types/functions: `PerfMetric` stores name, format code, numeric value, and averaged flag, with accessors, formatted output, prefixing, and serialization. `PerfIntCounter` and `PerfDoubleCounter` support increment/add, `getMetric()`, `getValue()`, and `clear()`, and can register themselves in caller-provided vectors.

Control flow: Counters accumulate locally until callers read `getMetric()` or clear them. Formatting uses the stored printf-style format string.

State and persistence behavior: Metric values are in-memory but `PerfMetric` serializes through Flow serializer using file identifier `5980618`. Counter objects are not themselves serialized here.

Dependencies and integration points: Depends on Flow BooleanParam, serialization, formatting, and `Averaged` parameter. Used by status/performance reporting surfaces that need a compact metric object independent of the richer `Stats.h` counters.

Risks: Format strings must match numeric value expectations. Vector registration stores raw counter pointers, so counter lifetime must outlive collection use. Averaging semantics are only a flag; consumers must interpret it consistently.

Test signals: Serialization round trips, formatted values, prefixing, integer no-decimal formatting, clear/increment behavior, and pointer registration lifetime in owning collections.
