# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/conf/TestRatisClientConfig.java

## Purpose
Validates defaults and mutability for `RatisClientConfig`, another typed HDDS Ratis client configuration bean.

## Important APIs, types, and functions
- Uses `OzoneConfiguration` typed object binding.
- Tests default values and setter/getter round trips for durations and retry-related client settings.

## Control flow
The tests instantiate the config object from a clean Ozone configuration, assert expected defaults, then set representative custom values and assert those values are returned.

## State and persistence behavior
State is local to the configuration object. There is no external persistence.

## Dependencies and integration points
The typed config is consumed by Ratis helper/client setup paths. The test protects the Ozone configuration framework to Java bean mapping.

## Risks and test signals
Incorrect defaults or property annotations can silently change client retry timing. The tests provide early detection of such mapping changes.
