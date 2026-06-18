# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosSubcommand.java

Purpose: `KerberosSubcommand` groups Kerberos debug commands under `ozone debug kerberos`.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, and declares `DiagnoseSubcommand` and `TranslatePrincipalSubcommand`.

Control flow: Picocli routes nested commands through this parent; the class contains no executable method.

State and persistence behavior: No state or persistence.

Dependencies and integration points: It integrates Kerberos diagnostics and principal translation into the extensible debug command tree.

Risks: Discovery depends on service metadata generated at compile time.

Test signals: Help/discovery for `diagnose` and `translate-principal` subcommands.
