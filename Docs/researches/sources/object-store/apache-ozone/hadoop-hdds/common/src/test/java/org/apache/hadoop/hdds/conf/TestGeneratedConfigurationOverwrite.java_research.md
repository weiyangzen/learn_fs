# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/conf/TestGeneratedConfigurationOverwrite.java

## Purpose
This test reproduces the HDDS-5035 classpath scenario where `hdds-common-default.xml` could be overwritten or absent in an assembled jar. It verifies annotated configuration objects still materialize using available defaults.

## APIs and dependencies
The class uses `Files.move`, `Path`, `Paths`, JUnit lifecycle hooks, `OzoneConfiguration`, and `SimpleConfiguration`. It manipulates `target/test-classes/hdds-common-default.xml` and a `.bak` path.

## Control flow and state behavior
Before each test, the generated config XML is renamed aside and a new `OzoneConfiguration` is created. After each test, the file is moved back. The test then calls `conf.getObject(SimpleConfiguration.class)` and asserts string, int, and time fields are non-null or non-zero. State mutation is local to the test build output directory and is restored after execution.

## Integration points
The test guards the interaction between generated configuration resources, annotation metadata, and runtime object construction. It is especially relevant for packaging, shaded jars, and classpath resource ordering.

## Risks and test signals
The test is filesystem-sensitive. If the generated file is missing before setup or recovery fails, later tests can be affected. Its signal is important because a packaging issue should not make basic annotated config injection unusable.
