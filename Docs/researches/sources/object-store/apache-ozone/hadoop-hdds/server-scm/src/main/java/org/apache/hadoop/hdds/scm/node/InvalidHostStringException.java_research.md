# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/InvalidHostStringException.java

Purpose: `InvalidHostStringException` is a checked exception used when `NodeDecommissionManager` cannot parse or understand a user-supplied host or `host:port` string.

Important APIs and types: It extends `IOException` and provides message-only and message-plus-cause constructors.

Control flow: There is no internal control flow. `NodeDecommissionManager.HostDefinition` throws it for invalid URI parsing or missing host components, and command paths convert it into `DatanodeAdminError`.

State and persistence behavior: The exception carries no additional state beyond standard exception message and cause. It has no persistence behavior.

Dependencies and integration points: It integrates decommission/maintenance host parsing with admin error reporting and existing IOException-based signatures.

Risks: The message text is user-visible through admin errors, so changes can affect CLI tests. Extending `IOException` means it can be grouped with network/lookup failures, which is convenient but can blur parse vs IO causes.

Test signals: Tests should cover invalid host strings, malformed URI inputs, blank host components, cause preservation, and conversion to `DatanodeAdminError`.
