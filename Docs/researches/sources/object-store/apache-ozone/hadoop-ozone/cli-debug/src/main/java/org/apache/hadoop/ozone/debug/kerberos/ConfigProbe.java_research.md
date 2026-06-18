# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/ConfigProbe.java

Purpose: `ConfigProbe` is the base class for Kerberos diagnostic probes, providing printing, warning/error, file-read validation, and krb5.conf resolution helpers.

Important APIs and types: It implements `DiagnosticProbe` indirectly, uses `OzoneConfiguration`, `File`, `Files.newInputStream`, and environment/system properties.

Control flow: `printValue` formats key/value lines, with special handling for auth-to-local output. `print` reads trimmed config values. `canReadFile` checks null, existence, regular file, readability, and non-empty content. `getKrb5ConfigFile` prefers JVM property, then `KRB5_CONFIG`, then `/etc/krb5.conf`.

State and persistence behavior: No persistence. It reads local filesystem metadata and environment/JVM state.

Dependencies and integration points: All Kerberos probes inherit these helpers, so output format and file validation behavior are centralized.

Risks: `File.canRead` plus opening catches most cases, but permissions can vary under different users. Special formatting tied to strings starting with `to Local user` is presentation-specific.

Test signals: Consistent WARNING/ERROR prefixes, correct krb5.conf precedence, and non-empty file validation.
