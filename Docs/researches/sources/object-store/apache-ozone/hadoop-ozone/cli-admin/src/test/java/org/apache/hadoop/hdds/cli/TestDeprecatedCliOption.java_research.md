<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/cli/TestDeprecatedCliOption.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/cli/TestDeprecatedCliOption.java

Purpose: Regression tests for warnings emitted when deprecated CLI options are used.

Important APIs and types: `ListPipelinesSubcommand`, Picocli `CommandLine`, custom execution strategy, captured `PrintStream` stderr, AssertJ assertions, and deprecated flags `-ffc`/`-fst` vs modern `--filter-by-factor`.

Control flow: Setup redirects stderr to a byte buffer. `createCommandLine` installs a stub execution strategy that returns OK without running real SCM behavior, so the tests focus on parsing/deprecation warnings. Tests execute one deprecated option, multiple deprecated options, and a modern long option.

State and persistence behavior: No persistence. Runtime state is captured stderr and restored system streams.

Dependencies and integration points: Validates shared CLI deprecation handling for Picocli commands in the admin module, using the pipeline list command as a representative command with deprecated hidden aliases.

Risks: Tests are sensitive to exact warning wording and option names. They do not verify exit codes beyond using an OK strategy.

Test signals: Stderr contains `WARNING: -ffc is deprecated, please use --filter-by-factor instead`, contains both warnings for two aliases, and is empty for the modern option.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/cli/TestDeprecatedCliOption.java -->
