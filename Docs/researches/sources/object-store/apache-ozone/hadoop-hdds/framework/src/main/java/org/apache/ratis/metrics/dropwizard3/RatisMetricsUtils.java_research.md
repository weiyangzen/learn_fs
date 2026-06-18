# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/ratis/metrics/dropwizard3/RatisMetricsUtils.java

## Purpose
`RatisMetricsUtils` is a small compatibility facade for Ratis Dropwizard3 metrics. It exposes the underlying Codahale `MetricRegistry` and JMX reporter registration callbacks needed by Ozone's HTTP/Prometheus metrics export code.

## Important APIs, Types, And Functions
`getDropWizardMetricRegistry(RatisMetricRegistry r)` casts the generic Ratis registry to `Dm3RatisMetricRegistryImpl` and returns its Dropwizard `MetricRegistry`.

`jmxReporter()` returns a `Consumer<RatisMetricRegistry>` that registers or starts JMX reporting through `Dm3MetricsReporting.jmxReporter()`. `stopJmxReporter()` returns the paired stopper consumer from `Dm3MetricsReporting.stopJmxReporter()`.

## Control Flow
There is no object lifecycle because this is an interface used only for static helpers. Callers obtain consumers and register them with `MetricRegistries.global()`, or convert a Ratis registry into a Dropwizard registry for Prometheus export. The methods do not catch exceptions; type or reporter failures propagate to the caller.

## State And Persistence
The utility stores no state. JMX reporter state and Dropwizard metric contents live in Ratis/Dropwizard registries outside this file. Persistence is limited to process-local metrics registration.

## Dependencies And Integration Points
Depends on Ratis metrics interfaces, Ratis Dropwizard3 implementation classes, Java `Consumer`, and Codahale `MetricRegistry`. `RatisDropwizardExports` uses all three methods to register JMX reporting and wrap Ratis registries as Prometheus collectors. `TestRatisDropwizardExports` validates the registry extraction path with `SegmentedRaftLogMetrics`.

## Risks
The unchecked cast to `Dm3RatisMetricRegistryImpl` is the central compatibility risk; any non-Dropwizard3 `RatisMetricRegistry` will fail with `ClassCastException`. The facade is also coupled to Ratis internal implementation class names, so Ratis upgrades can break binary or source compatibility. Reporter consumers must be removed symmetrically by callers to avoid stale global registrations.

## Test Signals
Metrics export tests should create real Ratis metrics, extract the Dropwizard registry, update a metric, and verify Prometheus output. Reporter lifecycle tests should add and remove JMX/Dropwizard reporters through `RatisDropwizardExports.clear` and confirm duplicate registration or unregister paths do not throw.
