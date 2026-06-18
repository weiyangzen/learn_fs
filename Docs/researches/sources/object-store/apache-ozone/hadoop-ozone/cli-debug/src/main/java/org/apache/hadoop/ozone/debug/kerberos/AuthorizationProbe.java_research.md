# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/AuthorizationProbe.java

Purpose: `AuthorizationProbe` diagnoses Ozone and Hadoop authorization configuration after basic Kerberos/security checks.

Important APIs and types: It extends `ConfigProbe`, returns `ProbeResult`, and reads config keys from `OzoneConfigKeys`, `CommonConfigurationKeysPublic`, `OMConfigKeys`, and `HddsConfigKeys`.

Control flow: The probe prints relevant security, authorization, ACL, and protocol ACL config values. It returns WARN when Ozone security is disabled, Ozone authorization is disabled, Hadoop service authorization is disabled, or Ozone ACL enforcement is disabled while authorization is otherwise enabled.

State and persistence behavior: It only reads `OzoneConfiguration` and writes diagnostics to stdout/stderr.

Dependencies and integration points: It runs within `DiagnoseSubcommand` and contributes to the aggregate PASS/WARN/FAIL summary.

Risks: Disabled security is treated as WARN rather than FAIL, appropriate for diagnostics but not enforcement. It prints values but does not validate ACL syntax.

Test signals: Printed config values and WARN/PASS classification for secure and non-secure configurations.
