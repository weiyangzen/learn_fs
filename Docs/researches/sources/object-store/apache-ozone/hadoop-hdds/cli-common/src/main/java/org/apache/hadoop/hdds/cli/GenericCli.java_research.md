# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/GenericCli.java

Purpose: Generic root implementation for Ozone command-line tools. It owns shared configuration loading, current-user lookup, execution strategy, dynamic subcommand registration, and concise error reporting.

Important APIs/types/functions: `execute` delegates to picocli, while `run` terminates nonzero exits through Ratis `ExitUtils`. Options include inherited `--verbose`, `-D/--set` configuration overrides, preferred `--conf`, and hidden deprecated `-conf`. `printError` chooses stack trace, ACL formatting, filesystem-specific messages, or the first error line. `getOzoneConf()` lazily adds the configured resource once. `getUser()` caches `UserGroupInformation`.

Control flow: Construction creates `CommandLine`, installs an execution exception handler, installs a strategy that warns for deprecated options then runs the last command, and dynamically adds service-loaded subcommands. During configuration lookup, `--conf` takes precedence over deprecated `-conf`.

State and persistence behavior: Holds one `OzoneConfiguration`, one picocli command, optional user, configuration path fields, and an "added" flag to avoid duplicate resource loading.

Dependencies and integration points: Core integration point for all Ozone CLIs built on picocli. Uses Hadoop `Path`, `HddsUtils`, `OzoneConfiguration`, UGI, `DeprecatedCliOption`, and `ExtensibleParentCommand`.

Risks: `printError` calls `ExitUtils.terminate` inside ACL handling, which can surprise tests unless exit trapping is configured. Configuration resources are added lazily, so code accessing `config` directly before `getOzoneConf()` would miss `--conf`. Error output truncates multiline messages unless verbose.

Test signals: Existing `TestGenericCliConfiguration` covers `--conf` versus `-conf` precedence. Additional signals include `-D` overrides, filesystem exception formatting, verbose stack traces, deprecated option warnings, and dynamic subcommand loading.
