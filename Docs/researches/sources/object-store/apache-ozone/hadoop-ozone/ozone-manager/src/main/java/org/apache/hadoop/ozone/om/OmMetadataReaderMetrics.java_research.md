# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataReaderMetrics.java

Purpose: `OmMetadataReaderMetrics` defines the metrics contract consumed by `OmMetadataReader` without tying it to one concrete metrics implementation.

Important APIs and types: it declares increment methods for key lookup, get-key-info, list status, file status, lookup file, key listing, ACL read, and object tagging operations, with separate failure increments for most operation families.

Control flow: none in the interface. Implementations decide whether increments map to counters, rates, or no-op behavior.

State and persistence: no state. Implementations are process-local metrics sources.

Dependencies and integration points: implemented by live OM metrics and snapshot metrics; injected into `OmMetadataReader`. This lets `OmSnapshot` reuse the reader while reporting to snapshot-specific metrics.

Risks: the interface has asymmetric success/failure coverage: `getAcl` has only a success increment and no failure method. Adding new read APIs requires updating both this interface and all implementations, or reads will be invisible to metrics.

Test signals: compile-time implementation coverage is important. Reader tests should verify the expected increment method fires for each success and failure branch.
