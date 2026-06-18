## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonReplicationOptions.java

Purpose: Freon-specific replication CLI mixin that extends shell `ReplicationOptions` and preserves legacy `--factor` support.

Important APIs/types/functions: options include deprecated `-F/--factor`, `--type/--replication-type`, and `--replication/-r`. Overrides setters and `fromParams(ConfigurationSource)`.

Control flow: when picocli parse result matched `--factor`, `fromParams` returns a RATIS replication config with the provided factor; otherwise it delegates to the generic replication options parser.

State and persistence behavior: stores parsed factor and picocli `CommandSpec`; no persistence.

Dependencies and integration points: used as `@Mixin` by key/file creation Freon commands. Depends on HDDS replication config classes and Ozone shell replication parsing.

Risks: legacy `--factor` forces RATIS regardless of other type options; precedence depends on picocli parse-result availability; default factor THREE may silently apply when `--factor` is matched without a value.

Test signals: parse combinations for `--replication`, `--type`, and `--factor`, including legacy behavior.
