# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMNodeStat.java

Purpose: mutable node storage statistic containing capacity, SCM used, remaining, committed, free space to spare, and reserved bytes.

Important APIs: default/copy/full constructors, metric getters, test-visible `set`, `add`, `subtract`, equality/hash, and `toString`.

Control flow and state: constructors and `set` validate capacity, used, and remaining are non-negative, but not committed, free space to spare, or reserved. Add/subtract mutate each `LongMetric` in place and can produce negative fields.

Dependencies and integration: wrapped by `SCMNodeMetric`, maintained by node manager, and used by placement/pipeline choice logic.

Risks: partial validation can allow negative committed/reserved/free-space values. `hashCode` XORs long values before `Long.hashCode`, which is adequate but coarse. Test signals should include copy independence, arithmetic, negative validation for all fields, and equality across all six metrics.
