# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/TranslatePrincipalSubcommand.java

Purpose: `TranslatePrincipalSubcommand` translates supplied Kerberos principals to local users using configured auth-to-local rules.

Important APIs and types: It extends `AbstractSubcommand`, implements `Callable<Integer>`, accepts one or more picocli parameters, and uses `KerberosName`.

Control flow: The command prints a header, reads `hadoop.security.auth_to_local` from Ozone config with default `DEFAULT`, installs the rules globally, then loops over principals. Each successful translation prints a PASS block; failures print an error to stderr and a FAIL block. Exit code is 1 if any principal fails.

State and persistence behavior: It reads configuration and mutates global KerberosName rules. No files are written.

Dependencies and integration points: It is a child of `KerberosSubcommand` and provides an operator-facing focused variant of `PrincipalMappingProbe`.

Risks: Global rule mutation can leak within a long-lived JVM. It does not validate krb5.conf readability before constructing `KerberosName`.

Test signals: Printed short names, PASS/FAIL counts, and non-zero return code when translation fails.
