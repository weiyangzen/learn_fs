# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KeytabProbe.java

Purpose: `KeytabProbe` validates configured service keytab files for Ozone components.

Important APIs and types: It extends `ConfigProbe`, reads keys from `OMConfigKeys`, `ScmConfig`, `HddsConfigKeys`, `ReconConfig`, and direct S3G config strings.

Control flow: The probe first checks Ozone security enabled. If disabled it returns WARN. Otherwise it iterates known keytab config keys; empty/unset paths are acceptable, but configured missing/unreadable/empty files mark FAIL. Valid files print `Keytab OK`.

State and persistence behavior: It reads configuration and filesystem state only.

Dependencies and integration points: It runs in the Kerberos diagnostic suite and covers OM, SCM, datanode, Recon, and S3G keytabs.

Risks: Security-enabled detection uses `Boolean.parseBoolean(conf.getTrimmed(...))` without the default helper, so unset config is treated as false. It does not inspect keytab contents beyond non-empty readability.

Test signals: WARN when security disabled, PASS when all configured keytabs are readable, FAIL when any configured keytab is missing or invalid.
