# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/JvmKerberosProbe.java

Purpose: `JvmKerberosProbe` validates JVM-level Kerberos system properties and effective krb5.conf readability.

Important APIs and types: It extends `ConfigProbe`, reads JVM properties `java.security.krb5.conf`, `java.security.krb5.realm`, `java.security.krb5.kdc`, and `sun.security.krb5.debug`.

Control flow: It prints all relevant properties, defaults missing krb5.conf to `/etc/krb5.conf`, validates file readability, warns on partial realm/KDC configuration, warns when explicit realm/KDC and krb5.conf are both set, and reports debug mode if enabled.

State and persistence behavior: It reads JVM properties and filesystem state only.

Dependencies and integration points: It runs before system Kerberos config and principal mapping probes in `DiagnoseSubcommand`.

Risks: Defaulting to `/etc/krb5.conf` differs from `ConfigProbe.getKrb5ConfigFile`, which also considers `KRB5_CONFIG`; that distinction can produce different diagnostics.

Test signals: FAIL on unreadable krb5.conf, WARN for partial/conflicting config, and PASS for readable consistent settings.
