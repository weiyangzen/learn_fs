<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/RotateKeySubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/RotateKeySubCommand.java

Purpose: Forces SCM secret-key rotation, optionally with `--force`.

Important APIs and types: `ScmSubcommand`, `ContainerOperationClient`, `ScmClient.rotateSecretKeys(boolean)`, parent `ScmAdmin`, and root command error printing.

Control flow: Although an SCM client is passed to `execute`, the command opens a new `ContainerOperationClient` from the root Ozone configuration. It calls `rotateSecretKeys(force)`, prints root error and returns on IOException, and prints success only when the returned status is true.

State and persistence behavior: No local persistence. Remote SCM key-manager state changes by generating a new key on success.

Dependencies and integration points: Registered under `ScmAdmin`; depends on SCM security/key rotation support and root configuration.

Risks: The supplied `scmClient` parameter is unused, which complicates tests and lifecycle expectations. IOExceptions are swallowed after printing, possibly preserving a success exit. False status produces no output.

Test signals: Force flag propagation, success output, false no-output behavior, IOException root error printing, and use of root configuration to create a new client.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/RotateKeySubCommand.java -->
