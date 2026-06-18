## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ShellReplicationOptions.java

Purpose: optional replication options for Ozone shell commands.

Important APIs and control flow: attaches non-required picocli options `--type`/`--replication-type`/`-t` and `--replication`/`-r` to the inherited setters in `ReplicationOptions`. Downstream commands decide whether empty parameters are allowed.

State and dependencies: inherited parse-time state only. Depends on `ReplicationOptions` and picocli.

Risks and test signals: consumers must call the appropriate resolver (`fromParams`, `fromParamsOrConfig`) and enforce requiredness when needed. `SetReplicationConfigHandler` enforces explicit parameters.
