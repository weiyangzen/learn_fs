# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/HddsVersionProvider.java

Purpose: Picocli version provider for HDDS/Ozone CLI commands.

Important APIs/types/functions: Implements `CommandLine.IVersionProvider`. `getVersion()` returns a one-element string array containing `HddsVersionInfo.HDDS_VERSION_INFO.getBuildVersion()`.

Control flow: Picocli invokes the provider when a command using it receives a version option.

State and persistence behavior: No state. It reads static build/version metadata from `HddsVersionInfo`.

Dependencies and integration points: Referenced by `AbstractSubcommand`'s `versionProvider`. Integrates CLI version output with HDDS build metadata.

Risks: If build metadata is missing or malformed, version output quality depends on `HddsVersionInfo`. The method declares `Exception` per picocli interface but does not handle failures.

Test signals: CLI `--version` output should include the expected HDDS build version.
