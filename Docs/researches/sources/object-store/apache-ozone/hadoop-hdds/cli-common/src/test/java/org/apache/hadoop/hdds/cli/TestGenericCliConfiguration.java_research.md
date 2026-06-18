# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/test/java/org/apache/hadoop/hdds/cli/TestGenericCliConfiguration.java

Purpose: Unit tests for `GenericCli` configuration-file option precedence, especially preferred `--conf` versus deprecated hidden `-conf`.

Important APIs/types/functions: `TestGenericCli` is an empty concrete subclass of `GenericCli`. Three JUnit 5 tests parse arguments and inspect `cli.getOzoneConf().get("test.key")`. `writeConf` creates temporary Hadoop XML configuration files with different values.

Control flow: Each test writes one or two temporary configs, parses arguments through picocli without executing a command, then lazily triggers config resource loading through `getOzoneConf()`. Assertions use AssertJ.

State and persistence behavior: Temporary files are created with `Files.createTempFile`, written as UTF-8 XML, and marked `deleteOnExit`. Each `GenericCli` has its own configuration state.

Dependencies and integration points: Tests the `GenericCli` path-selection logic and Hadoop `Configuration.addResource` parsing.

Risks: Tests rely on `deleteOnExit`, which can accumulate temp files in long-lived JVMs. They only cover configuration precedence, not warning emission for `-conf`.

Test signals: Confirms `--conf` wins when both options are present in either order, and deprecated `-conf` still works when preferred `--conf` is absent.
