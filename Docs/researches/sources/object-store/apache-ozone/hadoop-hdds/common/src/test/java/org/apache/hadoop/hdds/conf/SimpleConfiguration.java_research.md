# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/conf/SimpleConfiguration.java

## Purpose
`SimpleConfiguration` is a test-only annotated configuration bean used to validate Ozone's reflection-based configuration injection and extraction.

## APIs and dependencies
The class is annotated with `@ConfigGroup(prefix = "test.scm.client")` and extends `ReconfigurableConfig`. Fields use `@Config` metadata for string, boolean, int, time, `Duration`, class, and double values. It uses `ConfigType.TIME`, `ConfigType.CLASS`, `ConfigType.DOUBLE`, `ConfigTag`, `TimeUnit`, `Duration`, and `@PostConstruct`.

## Control flow and state behavior
When `OzoneConfiguration.getObject(SimpleConfiguration.class)` is called, the configuration framework reads annotated keys, parses types and units, populates fields, and invokes `validate()`. The post-construct validation rejects negative ports and wait times below 42 seconds. Setters and getters support reverse mapping via `setFromObject`. Reconfigurable fields include compression and wait time.

## Integration points
This bean is used by `TestOzoneConfiguration` and `TestGeneratedConfigurationOverwrite` to validate generated/default config metadata, object materialization, default values, duration conversion, class loading, and post-construction validation.

## Risks and test signals
The field `test.scm.client.compression.enabled` does not match one test's `test.scm.client.enabled` input, so tests implicitly distinguish object defaults from explicitly configured fields. Any change to annotations can break generated config files, reflection injection, or reconfiguration semantics.
