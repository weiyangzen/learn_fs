<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ConfigurationSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ConfigurationSubCommand.java

Purpose: picocli `config` subcommand that prints annotated Ozone configuration keys related to a selected insight point.

Important APIs: `call()` resolves the insight, prints a heading, derives component `Type` from the first dot-separated segment of the insight name, and invokes `showConfig` for each class returned by `InsightPoint.getConfigurationClasses`. `showConfig` creates a new `OzoneConfiguration`, loads remote component config through `getHost(conf, new Component(type)) + "/conf"`, and delegates to `printConfig`. `printConfig` requires a class-level `@ConfigGroup`, scans declared fields only, and prints `@Config` key, default, current value, and description.

Control flow and integration: this subcommand integrates the insight catalog with HDDS config annotations and component HTTP `/conf`. It currently reports only direct declared fields in annotated classes, despite the method comment mentioning superclasses.

State and persistence: no persistent state; remote `/conf` is loaded as an OzoneConfiguration resource for display.

Risks and tests: deriving `Type` from the insight-name prefix assumes all names start with enum-compatible labels. `showConfig` uses a fresh configuration, so address resolution may rely on defaults or local site resources rather than the parent command's exact configuration. It does not URL-authenticate itself; resource loading depends on Hadoop configuration support. `TestConfigurationSubCommand` covers `printConfig` output for `OmConfig`, but not remote `/conf` loading or superclass scanning.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ConfigurationSubCommand.java -->
