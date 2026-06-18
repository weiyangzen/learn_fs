# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/PerformanceMetricsInitializer.java

## Purpose

`PerformanceMetricsInitializer` is the reflection helper that initializes annotated `PerformanceMetrics` fields in a metrics source.

## APIs and control flow

`initialize(source, registry, sampleName, valueName, intervals)` scans declared fields on the source's concrete class. For fields whose type is exactly `PerformanceMetrics` and that carry a Hadoop `@Metric` annotation, it creates a `PerformanceMetrics` instance using the field name and annotation description, sets the field accessible, writes the instance into the source object, and records it in a map keyed by field name.

## State, dependencies, and integration

The class is stateless. It depends on Java reflection, Hadoop metrics annotations, and `MetricsRegistry`. It integrates with `PerformanceMetrics.initializeMetrics`.

## Risks and test signals

Only declared fields on the concrete class are scanned; inherited fields are ignored. Existing field values are overwritten. Tests should cover private field injection, multiple fields, ignored unannotated or subclassed fields, inherited-field behavior, and access failure propagation.
