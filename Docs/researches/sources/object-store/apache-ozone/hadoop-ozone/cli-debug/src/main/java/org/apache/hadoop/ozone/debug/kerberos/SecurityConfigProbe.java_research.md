# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/SecurityConfigProbe.java

Purpose: `SecurityConfigProbe` prints and validates high-level Hadoop/Ozone security settings.

Important APIs and types: It extends `ConfigProbe`, reads Hadoop authentication/RPC protection/SASL resolver settings plus Ozone security, HTTP security, admin, token, and TLS keys.

Control flow: The probe prints all relevant keys, then warns if Hadoop auth is not Kerberos or Ozone security is not enabled. It returns PASS only when both primary settings are enabled.

State and persistence behavior: It reads `OzoneConfiguration` only.

Dependencies and integration points: It runs before authorization and HTTP auth probes in the Kerberos diagnostic flow.

Risks: It treats all non-Kerberos auth values as WARN, not FAIL. The warning for Ozone security prints `false` literally rather than the actual config string.

Test signals: Config printout and WARN/PASS classification based on auth and Ozone security booleans.
