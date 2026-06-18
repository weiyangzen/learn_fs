## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationConfigValidator.java

Purpose: configuration-backed validator restricting allowed replication configs by regex.

Important APIs: `disableValidation`, `setValidationPattern`, `init` as `@PostConstruct`, and `validate`. The default pattern allows STANDALONE/RATIS ONE or THREE and selected EC data/parity/chunk combos.

Control flow: pattern changes trigger recompilation; empty or null pattern disables validation. `validate` compares `replicationConfig.configFormat()` against the compiled pattern and throws `IllegalArgumentException` on mismatch.

State/persistence: holds configured pattern and compiled `Pattern`. Dependencies: HDDS config annotations and Java regex. Integration points: `ReplicationConfig.parseWithoutFallback`, generated config XML, admin controls for allowed replication schemes.

Risks: regex is an operational policy surface; overly restrictive patterns can block writes, overly permissive patterns can admit unsupported layouts. Pattern syntax errors surface during config object initialization or setter use. Test signals: default allowed/disallowed matrix, disabling validation, setter recompilation, invalid regex handling, and exception message containing pattern.
