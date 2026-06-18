## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonHttpServer.java

Purpose: HTTP/HTTPS server wrapper for Freon metrics and profiling endpoints.

Important APIs/types/functions: extends `BaseHttpServer`. Overrides configuration key accessors for HTTP/HTTPS addresses, bind hosts, default ports, Kerberos keytab/principal, enabled key, auth type, and auth config prefix.

Control flow: constructed by `Freon.startHttpServer(conf)` when `--server` is enabled. Base class owns actual server lifecycle.

State and persistence behavior: no independent state beyond base HTTP server internals. Runtime effects are listening sockets and metrics/profile endpoints.

Dependencies and integration points: uses `MutableConfigurationSource`, HDDS `BaseHttpServer`, and Freon-specific keys from `OzoneConfigKeys`.

Risks: config-key correctness is critical; bad bind address or Kerberos settings cause startup failures that Freon logs but does not propagate.

Test signals: with `--server`, Freon should bind using `ozone.freon.*` HTTP config defaults and expose base endpoints.
