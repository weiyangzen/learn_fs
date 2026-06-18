## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/HddsPrometheusConfig.java

Purpose: configuration bean for the HDDS Prometheus servlet endpoint.

Important APIs: annotated field `hdds.prometheus.endpoint.token`, getter and setter. The description states a configured token allows token authorization and disables SPNEGO-based authentication for the endpoint.

Control flow/state: mutable bean field populated by config injection. Dependencies: HDDS config annotations. Integration points: generated config XML and Prometheus servlet authentication setup.

Risks: token presence changes authentication mode; empty default means no token. Token storage and logging must be handled carefully by consumers. Test signals: config binding, default empty token, and endpoint authentication mode selection.
