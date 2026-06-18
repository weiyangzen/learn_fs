<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestConfigurationSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestConfigurationSubCommand.java

Purpose: unit test for configuration annotation printing.

Important APIs: redirects stdout in `@BeforeEach`, restores in `@AfterEach`, creates an `OzoneConfiguration` with a custom `OmConfig.Keys.SERVER_LIST_MAX_SIZE`, invokes `ConfigurationSubCommand.printConfig(OmConfig.class, conf)`, and asserts output contains expected keys, defaults, current custom/default values, and descriptions indirectly through key output.

Control flow and test signals: confirms `printConfig` reads `@Config` metadata and current configuration values for declared fields on an annotated class.

State and persistence: mutates JVM `System.out` for the test duration. No persistence.

Dependencies and integration: AssertJ, JUnit 5, `OmConfig`, `OzoneConfiguration`.

Risks and gaps: does not test classes without `@ConfigGroup`, inherited fields, remote `/conf` loading, or picocli `call()` behavior. Static stdout redirection can interfere with parallel tests if not isolated.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestConfigurationSubCommand.java -->
