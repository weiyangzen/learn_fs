# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/RatisDropwizardExports.java

Purpose: `RatisDropwizardExports` adapts Ratis Dropwizard metrics for Prometheus while using Ozone's Ratis-specific name rewrite builder.

Important APIs/types/functions: constructor passes a `MetricRegistry` and `RatisNameRewriteSampleBuilder` to Prometheus `DropwizardExports`. `registerRatisMetricReporters()` installs JMX and Prometheus reporter registrations into Ratis global metric registries. `clear()` unregisters collectors and removes global reporter registrations. `getName()` builds a Dropwizard registry name from `MetricRegistryInfo`. Private register/deregister methods manage `CollectorRegistry.defaultRegistry`.

Control flow: registration creates two `MetricReporter` wrappers, adds them globally, and future Ratis metric registry creation invokes reporter consumers. The Prometheus reporter creates a `RatisDropwizardExports` for each registry unless the supplied stopped check is true, stores it by name, and registers it with the default collector registry. Deregistration removes and unregisters the collector.

State and persistence: caller-supplied map stores active exports; reporter list stores global registrations. No durable state.

Dependencies/integration: depends on Ratis metrics APIs, Dropwizard metrics, Prometheus Java client, and `RatisNameRewriteSampleBuilder`. `PrometheusServlet` emits the default registry that these collectors populate.

Risks: `clear()` removes while streaming over `entrySet()`, which can be fragile depending on map implementation. CollectorRegistry unregistering a non-registered collector can throw, so map discipline matters. Global Ratis registry side effects must be cleaned between tests/servers.

Test signals: `TestRatisNameRewrite` covers sample normalization. Prometheus integration tests exercise default registry output; Ratis metrics paths provide broader integration coverage.
