<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Insight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Insight.java

Purpose: top-level hidden picocli command `ozone insight` for inspecting Ozone component logs, metrics, and configuration.

Important APIs: annotated with `@CommandLine.Command`, `hidden = true`, `HddsVersionProvider`, standard help options, and subcommands `ListSubCommand`, `LogSubcommand`, `MetricsSubCommand`, and `ConfigurationSubCommand`. It extends `GenericCli`, inheriting Ozone configuration and command execution behavior. `main` simply constructs `Insight` and runs the supplied args.

Control flow and integration: command-line entry flows through `GenericCli.run`, picocli dispatch, and child subcommands. The parent command supplies `getOzoneConf()` to `BaseInsightSubCommand`.

State and persistence: no local state beyond GenericCli-managed configuration. No persistence.

Risks and tests: because the command is hidden, discoverability depends on explicit use. Failures in subcommands will surface through GenericCli/picocli handling. There is no direct integration test of `Insight.main`; subcommand helper behavior is tested separately.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/Insight.java -->
