# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosTicketProbe.java

Purpose: `KerberosTicketProbe` checks whether Hadoop is configured for Kerberos and whether the current process has active Kerberos credentials.

Important APIs and types: It extends `ConfigProbe`, uses `UserGroupInformation`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_AUTHENTICATION`, and `KRB5CCNAME`.

Control flow: The probe sets UGI configuration, checks whether authentication is `kerberos`, warns if not, reads the login user and auth method, checks `hasKerberosCredentials`, prints ticket cache information, and returns WARN for inactive/missing credentials or PASS for a valid Kerberos login.

State and persistence behavior: It mutates process-global UGI configuration and reads current login/ticket state; no files are written.

Dependencies and integration points: It is part of the diagnostic suite and interacts with Hadoop security runtime state.

Risks: `UserGroupInformation.setConfiguration` is global and can affect later security checks in the same JVM. Ticket cache visibility depends on process environment.

Test signals: WARN for simple auth, WARN for Kerberos config without active ticket, PASS for valid Kerberos credentials, FAIL on UGI exceptions.
