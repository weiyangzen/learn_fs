# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/conf/TestConfigurationFieldsBase.java

## Purpose

`TestConfigurationFieldsBase` is an abstract JUnit 5 test base copied from Hadoop while the original was still JUnit 4 based. Subclasses set an XML defaults file and one or more configuration classes, and this base compares public static final configuration-key constants against XML properties and default-value constants.

It is a configuration hygiene guard: it detects config keys missing from XML docs/defaults, XML properties missing from configuration classes, mismatched XML default values, XML properties with empty values, config keys with no default constant, and selected default-value collisions such as duplicate service ports.

## Important APIs, Types, and Functions

- Subclasses implement `initializeMemberVariables()` and set `xmlFilename`, `configurationClasses`, optional error flags, skip sets, prefix skip sets, and `filtersForDefaultValueCollisionCheck`.
- `extractMemberVariablesFromConfigurationFields(Field[])` reflects over public static final `String` fields, skips default-value fields, partial/file-like values, configured skip entries/prefixes, and values that do not match the property-name regex.
- `extractPropertiesFromXml(String)` loads an XML resource into `Configuration(false)`, enables null-value properties, iterates key/value pairs, applies XML skip lists, and records null for key-only properties.
- `isFieldADefaultValue(Field)` identifies default constants by `DEFAULT_` prefix or `_DEFAULT` suffix.
- `extractDefaultVariablesFromConfigurationFields(Field[])` reflects over public static final default constants and serializes supported primitive/String types into strings.
- `compareConfigurationToXmlFields(Map, Map)` performs key-set difference.
- `setupTestConfigurationFields()` is a `@BeforeEach` method that calls subclass initialization, extracts maps, and computes missing-key sets.
- JUnit tests `testCompareConfigurationClassAgainstXml`, `testCompareXmlAgainstConfigurationClass`, `testXmlAgainstDefaultValuesInConfigurationClass`, and `testDefaultValueCollision` report and optionally fail on discovered mismatches.

## Control Flow

Each test begins with `setupTestConfigurationFields()`. The setup asserts subclass configuration is present, builds `configurationMemberVariables` by reflecting all declared fields of all configured classes, builds `xmlKeyValueMap` through Hadoop `Configuration` resource parsing, builds `configurationDefaultVariables`, then computes the two missing-key sets.

`testCompareConfigurationClassAgainstXml` logs configuration keys not present in XML and fails only when `errorIfMissingXmlProps` is true. `testCompareXmlAgainstConfigurationClass` logs XML properties without matching config constants and fails only when `errorIfMissingConfigProps` is true.

`testXmlAgainstDefaultValuesInConfigurationClass` derives possible default constant names in three patterns: `DEFAULT_` plus key constant name, replacing `_KEY` with `_DEFAULT`, and appending `_DEFAULT`. It then classifies XML properties as matching defaults, mismatching defaults, empty XML values, or having no default constant. This test logs findings but does not assert by default.

`testDefaultValueCollision` iterates requested name filters, gathers numeric default values whose constant names contain the filter, and asserts no duplicate numeric default value appears under that filter.

## State and Persistence Behavior

The class stores extracted maps and missing sets in private instance fields per test instance. Because setup runs before each test, state is recomputed from the subclass-provided class list and XML file and is not persisted outside the test object. XML loading is read-only, and reflection reads static constants without mutating target classes.

The only external side effects are logs through `LOG`, `LOG_CONFIG`, and `LOG_XML`, plus JUnit assertion failures when strict flags or collision checks detect violations.

## Dependencies and Integration Points

The file depends on Hadoop `Configuration`, Java reflection APIs, regex utilities, collection types, Commons Lang `StringUtils`, SLF4J, and JUnit 5. It integrates with Ozone/Hadoop configuration classes through reflection and with XML defaults files through Hadoop resource parsing.

Subclasses across the integration-test module can tune behavior by adding exact-key or prefix skips for generated, deprecated, private, partial, or intentionally undocumented properties.

## Risks and Edge Cases

- Property detection uses a regex that requires dotted names starting with a letter; valid but unusual configuration names outside that pattern will be ignored.
- Default matching depends on naming conventions, so semantically correct defaults with nonstandard constant names are reported as requiring manual verification.
- Duplicate config-key values across classes are logged but not failed directly in extraction.
- `Configuration` resource loading can include substitution or inherited behavior from Hadoop configuration parsing, so XML comparison is not a raw XML parse.
- `HashMap<HashMap<String,String>, HashMap<String,String>>` for mismatches is awkward and can obscure duplicate mismatch reporting, though it is only used for logs.
- Failure behavior is controlled by subclass flags; without strict flags, missing config/XML entries are informational rather than test-failing.

## Test Signals

The strongest test signals are strict missing-key assertions when enabled, null/non-null setup assertions, default numeric collision assertions, and detailed logs listing missing or mismatching entries. The class supports broad configuration documentation consistency tests rather than exercising Ozone runtime behavior.
