# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMHTTPServerConfig.java

Purpose: `SCMHTTPServerConfig` is the Java-style configuration bean for SCM HTTP server SPNEGO/Kerberos authentication settings.

Important APIs and types: It is annotated with `@ConfigGroup(prefix = "hdds.scm.http.auth")`. Config fields are the HTTP Kerberos principal and keytab path. Getters and setters expose both values. Nested `ConfigStrings` publishes full legacy-compatible key names for code that needs string constants.

Control flow: There is no runtime control flow beyond simple getters and setters. The configuration framework populates annotated fields from `OzoneConfiguration`.

State and persistence behavior: The object holds configuration values in memory. Persistence comes from external configuration files.

Dependencies and integration points: It integrates with the HDDS configuration annotation system, Kerberos/SPNEGO HTTP server setup, and older code paths that reference raw config keys.

Risks: The annotation keys include the full property names while the config group also has a prefix; compatibility should be checked against the configuration framework's expected key composition. Defaults include placeholder realm and standard keytab path that must be overridden in secure deployments.

Test signals: Tests should verify configuration binding, default values, setter/getter behavior, and `ConfigStrings` key values used by HTTP security setup.
