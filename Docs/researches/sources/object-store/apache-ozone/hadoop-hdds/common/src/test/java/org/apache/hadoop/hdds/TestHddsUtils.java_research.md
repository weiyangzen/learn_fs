# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/TestHddsUtils.java

## Purpose
`TestHddsUtils` verifies utility behavior for host parsing, path ancestry validation, numeric config lookup, and redaction of sensitive configuration values before logging.

## APIs and dependencies
The tests target `HddsUtils.getHostName`, `HddsUtils.validatePath`, `HddsUtils.getNumberFromConfigKeys`, and `HddsUtils.processForLogging`. They use `OzoneConfiguration`, SCM config keys, `ConfUtils.addKeySuffixes`, Hadoop's sensitive config key list, JUnit 5 assertions, and parameterized argument sources.

## Control flow and state behavior
Host parsing checks `host:port`, bare host, and missing host cases. Path validation checks normalized descendants against ancestors and rejects traversal or unrelated paths. Numeric config lookup first reads a single configured key, then verifies first-present behavior across service/node-suffixed and fallback keys. Redaction configures sensitive regex suffixes and confirms matching password/key properties are replaced with `<redacted>` while unrelated properties remain visible.

## Integration points
These utilities are used across daemon startup, filesystem/path safety, HA key lookup, logging, and supportability. The redaction test integrates with Hadoop's `hadoop.security.sensitive-config-keys` mechanism.

## Risks and test signals
Path normalization is security-sensitive because bad ancestry checks can allow escapes. Logging redaction is operationally sensitive because false negatives leak secrets and false positives hide useful diagnostics. Config-key lookup order is compatibility-sensitive for HA and service-specific overrides.
