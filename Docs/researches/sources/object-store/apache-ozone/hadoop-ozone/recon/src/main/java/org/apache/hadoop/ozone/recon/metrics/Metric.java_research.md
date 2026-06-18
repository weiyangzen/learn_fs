## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/Metric.java

Purpose: simple immutable-ish wrapper for a metric response from `MetricsServiceProvider`.

Important APIs/types/functions: constructor accepts metadata map and sorted values; `getMetadata`; `getValues`.

Control flow: constructor copies values into a `TreeMap` to enforce sorted numeric timestamp/value ordering.

State and persistence: no persistence; metadata map reference is retained, values map is internally copied. Integration is with Recon metrics API/service responses.

Risks: metadata is not defensively copied and values getter returns the mutable `TreeMap` as `SortedMap`, allowing caller mutation. Tests should cover ordering, empty values, metadata preservation, and mutability expectations.
