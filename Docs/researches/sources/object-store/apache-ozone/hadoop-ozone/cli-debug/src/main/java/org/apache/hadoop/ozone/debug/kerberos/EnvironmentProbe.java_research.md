# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/EnvironmentProbe.java

Purpose: `EnvironmentProbe` prints environment variables relevant to Kerberos and Ozone configuration discovery.

Important APIs and types: It extends `ConfigProbe` and reads process environment through `System.getenv`.

Control flow: `test()` prints `KRB5_CONFIG`, `KRB5CCNAME`, `OZONE_CONF_DIR`, `HADOOP_CONF_DIR`, and `JAVA_SECURITY_KRB5_CONF`, then returns PASS.

State and persistence behavior: It reads environment variables only and does not persist or mutate state.

Dependencies and integration points: It supplies context early in `DiagnoseSubcommand` for later file/config failures.

Risks: It does not validate whether paths exist or whether `JAVA_SECURITY_KRB5_CONF` maps to an actual JVM property; it is informational.

Test signals: Output lines for all expected environment variable names and PASS result.
