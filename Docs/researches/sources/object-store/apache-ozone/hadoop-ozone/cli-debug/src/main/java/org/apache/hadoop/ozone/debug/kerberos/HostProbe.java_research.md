# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/HostProbe.java

Purpose: `HostProbe` reports basic host, user, and Java runtime information for Kerberos troubleshooting.

Important APIs and types: It extends `ConfigProbe`, uses `InetAddress.getLocalHost().getCanonicalHostName`, and JVM system properties.

Control flow: It attempts hostname resolution, user-name lookup, and Java-version lookup independently. Hostname or user failures mark FAIL; Java-version failure can downgrade PASS to WARN.

State and persistence behavior: It reads host/JVM state only.

Dependencies and integration points: It is the first probe in `DiagnoseSubcommand`, establishing local process context.

Risks: Hostname resolution can block or fail based on DNS/hosts configuration; this is intentionally surfaced as FAIL.

Test signals: Printed hostname, user, Java version, and correct PASS/WARN/FAIL classification under simulated failures.
