# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/GenericParentCommand.java

Purpose: Shared interface exposed by CLI root commands to subcommands and mixins.

Important APIs/types/functions: Declares `isVerbose()`, `getOzoneConf()`, `getUser()`, and `printError(Throwable)`. The contract specifies cached configuration and cached `UserGroupInformation`.

Control flow: `AbstractSubcommand` and `AbstractMixin` resolve their root as this interface and delegate common behavior to it.

State and persistence behavior: Interface has no state, but implementations such as `GenericCli` own the configuration and user cache.

Dependencies and integration points: Bridges CLI command classes to `OzoneConfiguration` and Hadoop security without requiring a concrete `GenericCli` dependency.

Risks: Implementations need consistent caching and error semantics. A test fallback implementation exists in `AbstractSubcommand`, so behavior can differ from production root command behavior.

Test signals: Subcommand unit tests should verify calls through this interface observe the intended root implementation.
