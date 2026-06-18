# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ha/ConfUtils.java

## Purpose

`ConfUtils` contains HA-related configuration-key helpers, mainly for deriving and applying node-specific keys such as `<key>.<serviceId>.<nodeId>`.

## APIs and control flow

`addSuffix` appends a non-empty suffix with a dot separator and asserts the suffix is not already dotted. `addKeySuffixes` concatenates suffixes and appends them to a base key. `concatSuffixes` uses Guava `Joiner` with skipped nulls. `getConfSuffixedWithServiceId` reads a trimmed node-specific config and returns null for empty values. `setNodeSpecificConfigs` loops over configured keys, reads node-specific values, logs the mapping, and writes the generic key into `OzoneConfiguration`.

## State, dependencies, and integration

The class is stateless. It depends on Guava, Apache Commons `StringUtils`, HDDS configuration interfaces, `OzoneConfiguration`, and SLF4J. It integrates with HA service startup code that resolves OM/SCM node-specific settings.

## Risks and test signals

`addSuffix` uses Java `assert`, so dotted-suffix validation is disabled unless assertions are enabled. Empty strings from skipped suffixes can produce unexpected keys. Tests should cover null suffixes, multiple suffix joins, missing config fallback, and mutation of generic keys during service initialization.
