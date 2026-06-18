# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/PrincipalMappingProbe.java

Purpose: `PrincipalMappingProbe` validates Hadoop auth-to-local rules against configured Ozone service principals.

Important APIs and types: It extends `ConfigProbe`, uses `KerberosName`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_AUTH_TO_LOCAL`, and service principal config keys for OM, SCM, datanode, Recon, and S3G.

Control flow: The probe first validates the effective krb5.conf file, prints auth-to-local rules, installs them with `KerberosName.setRules`, gathers configured principals, and attempts to translate each to a local short name. Missing principals return WARN; individual mapping failures downgrade to WARN.

State and persistence behavior: It reads configuration and filesystem state and mutates global `KerberosName` rules.

Dependencies and integration points: It is part of Kerberos diagnosis and complements `TranslatePrincipalSubcommand`.

Risks: Global KerberosName rule mutation can affect later code in the JVM. Principal strings containing `_HOST` may not map as expected without substitution.

Test signals: Printed principal-to-local mappings, WARN for no principals or per-principal failures, FAIL for unreadable krb5.conf.
