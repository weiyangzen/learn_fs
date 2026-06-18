<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/PerfMetric.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/PerfMetric.java

## Purpose
`PerfMetric` is a mutable Java bean for reporting named workload performance metrics.

## Important APIs, Types, And Functions
It stores `name`, `value`, `averaged`, and `formatCode`. Constructors default `averaged` to true and format to `"%.3g"`, with getters and setters for every field.

## Control Flow, State, And Persistence
There is no control flow beyond construction and property access. Persistence/reporting happens in the external workload harness that consumes instances from `AbstractWorkload.getMetrics`.

## Dependencies And Integration Points
It is used by Java workload implementations and native test infrastructure to collect metrics.

## Risks And Test Signals
Risks include invalid format strings, mutable metrics being changed after collection, and lack of units. Tests should check default constructor behavior, custom averaged/format settings, and harness formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/PerfMetric.java -->
