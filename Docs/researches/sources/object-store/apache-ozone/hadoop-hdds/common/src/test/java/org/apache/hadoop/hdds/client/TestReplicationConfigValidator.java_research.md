# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/client/TestReplicationConfigValidator.java

## Purpose
This class verifies `ReplicationConfigValidator`, the component that enforces the allowed replication configuration set from configuration.

## APIs and dependencies
The tests use `InMemoryConfigurationForTesting`, `MutableConfigurationSource`, `ReplicationConfigValidator`, `ECReplicationConfig`, `RatisReplicationConfig`, `StandaloneReplicationConfig`, EC codecs, and protobuf replication factors ONE, THREE, and ZERO. JUnit's per-class lifecycle allows validators to be initialized once in `@BeforeAll`.

## Control flow and state behavior
Setup builds a default validator and a disabled validator by setting `ozone.replication.allowed-configs` to an empty string. `validConfigsForEC` generates every accepted EC combination across codecs, data/parity pairs 3-2, 6-3, 10-4, and chunk sizes 512 KB, 1 MB, 2 MB, and 4 MB. Default validation accepts RATIS and STANDALONE ONE/THREE plus valid EC strings, and rejects invalid EC data/parity or chunk sizes. Disabled validation accepts otherwise invalid EC combinations and also accepts standalone ZERO. A custom validator set to `RATIS/THREE` accepts only that replicated config.

## Integration points
The validator is used by replication parsing and default selection to restrict new writes while allowing administrators to disable validation when needed.

## Risks and test signals
The critical risk is rejecting valid production layouts or permitting unsupported EC layouts by default. The disabled-validator path is also intentional and should remain explicit because it can allow legacy or unsafe configs.
