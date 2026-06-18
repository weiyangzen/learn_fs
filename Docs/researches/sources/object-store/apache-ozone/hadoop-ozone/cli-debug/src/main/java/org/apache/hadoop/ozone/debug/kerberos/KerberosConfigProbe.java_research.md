# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosConfigProbe.java

Purpose: `KerberosConfigProbe` validates system-level krb5.conf availability and default realm resolution.

Important APIs and types: It extends `ConfigProbe`, reads `KRB5_CONFIG`, uses `KerberosUtil.getDefaultRealm`, and validates a `File`.

Control flow: The probe chooses `KRB5_CONFIG` or `/etc/krb5.conf`, prints the path, checks that it is readable and non-empty, then prints the default realm or returns FAIL on resolution errors.

State and persistence behavior: It reads environment, filesystem, and Kerberos library state only.

Dependencies and integration points: It provides foundational Kerberos config validation for the diagnosis sequence.

Risks: It ignores the JVM `java.security.krb5.conf` property, unlike `ConfigProbe.getKrb5ConfigFile`, so results may differ from JVM probe behavior.

Test signals: PASS with readable config and resolvable default realm; FAIL for missing/unreadable file or realm lookup failure.
