# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AbstractSubcommand.java

Purpose: Shared base class for Ozone picocli subcommands. It provides access to root command context, output streams, verbose mode, configuration, and a unit-test fallback root.

Important APIs/types/functions: Picocli injects `CommandSpec`. `rootCommand()` memoizes `findRootCommand(spec)` through Ratis `MemoizedSupplier`. `isVerbose()`, `getOzoneConf()`, `out()`, and `err()` delegate to root or command line streams. `NoParentCommand` supplies a default `OzoneConfiguration`, current user lookup, and stack-trace error printing for tests that bypass `GenericCli`.

Control flow: Subcommands are executed by picocli with standard help options and `HddsVersionProvider`. On first root access, the class checks whether the root user object implements `GenericParentCommand`; otherwise it installs the fallback.

State and persistence behavior: Holds injected command spec and a memoized root supplier. The fallback root lazily caches `UserGroupInformation`.

Dependencies and integration points: Used by concrete Ozone CLI commands. Depends on picocli, `GenericParentCommand`, Hadoop security, and Ozone configuration.

Risks: Directly constructed subcommands need a spec before helper methods are safe. The fallback can hide missing root command setup in tests, so integration tests should also run through `GenericCli`.

Test signals: Command execution tests should verify inherited version/help options, stdout/stderr routing, fallback behavior, and root configuration propagation.
