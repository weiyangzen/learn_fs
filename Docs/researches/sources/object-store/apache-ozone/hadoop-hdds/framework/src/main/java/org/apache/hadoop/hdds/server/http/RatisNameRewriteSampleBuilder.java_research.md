# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/RatisNameRewriteSampleBuilder.java

Purpose: `RatisNameRewriteSampleBuilder` rewrites Ratis Dropwizard metric names into Prometheus samples with useful labels for instance, group, and follower identity.

Important APIs/types/functions: constructor initializes follower regex patterns. `createSample()` intercepts metrics whose Dropwizard name starts with Ratis's metrics application prefix, calls `normalizeRatisMetric()`, and delegates to `DefaultSampleBuilder`; non-Ratis metrics are delegated unchanged. `normalizeRatisMetric()` splits dotted name parts, moves the second identifier segment into `instance`/`group` labels, and extracts follower ids from known follower metric forms.

Control flow: Prometheus Dropwizard export calls `createSample()` for each metric. Ratis metric names are normalized before sample creation and trace-logged when enabled.

State and persistence: immutable pattern list after construction; no persisted state.

Dependencies/integration: used by `RatisDropwizardExports`. Depends on Prometheus client Dropwizard sample builder, Ratis metrics prefix, Commons Lang `StringUtils`, regex, and SLF4J.

Risks: regex/name-shape assumptions are specific to current Ratis metric naming. Changes in Ratis names may lose labels or generate unexpected metric names. Labels are appended to existing additional labels, so duplicate label names could occur if upstream uses the same names.

Test signals: `TestRatisNameRewrite` validates normalization of Ratis metric names, including instance/group/follower extraction.
