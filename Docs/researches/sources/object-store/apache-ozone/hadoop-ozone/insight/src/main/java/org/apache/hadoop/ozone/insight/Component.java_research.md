<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Component.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Component.java

Purpose: value object identifying the Ozone component instance that owns metrics or logs.

Important APIs: constructors accept `Type`, optional `id`, optional `hostname`, and optional HTTP port. Getters expose those fields. `prefix()` produces display prefixes such as `SCM` or `DATANODE-uuid`. Equality and hash code use only `name` and `id`, intentionally ignoring hostname and port. `Type` enumerates `SCM`, `OM`, `DATANODE`, `S3G`, and `RECON`.

Control flow and integration: `MetricGroupDisplay` and `LoggerSource` embed `Component`. `BaseInsightSubCommand.getHost` either resolves SCM/OM HTTP endpoints from config or uses a component-specified datanode hostname/port. `LogSubcommand` de-duplicates log streaming sources with a `Set<Component>`, so equality semantics matter.

State and persistence: immutable in practice because there are no setters, though fields are not final. No persistence.

Risks and tests: because equality ignores host and port, two datanode components with the same id but different host or port collapse in sets/maps. For ad-hoc datanode filters where id is null, all `DATANODE` components compare equal, which can suppress multiple streams if used together. No direct unit test covers equality or prefix behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Component.java -->
