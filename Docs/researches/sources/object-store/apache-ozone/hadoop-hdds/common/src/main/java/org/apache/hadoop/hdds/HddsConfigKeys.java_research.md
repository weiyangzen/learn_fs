## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/HddsConfigKeys.java

Purpose: central constant holder for HDDS configuration keys and defaults. It groups heartbeat/report intervals, SCM safe mode thresholds, metadata directory fallback, key/certificate material names, token and CA rotation durations, gRPC TLS knobs, security ACL keys, datanode HTTP/client/Ratis/checksum/disk-balancer settings, DNS and hostname settings, X-Frame options, metrics keys, and Kerberos keytab/principal keys.

Important APIs/types/functions: all exported behavior is public static constants; the private constructor prevents instantiation. Downstream classes import these constants directly, including `HddsUtils`, `OzoneConfiguration`, `RatisHelper`, service configuration beans, datanode services, security modules, and compatibility deprecation mapping.

Control flow: none beyond class loading. State/persistence: no mutable state, but values define persisted config names and default behavior for cluster services. Dependencies: no runtime dependencies beyond Java.

Integration points: Hadoop/Ozone XML configuration, datanode startup, SCM safe mode, certificate/key stores, gRPC TLS, token enforcement, and HTTP security. Risks: renaming or changing defaults has cluster-wide compatibility impact; time strings must match Hadoop duration parsing; defaults like token disabled and bind host `0.0.0.0` are security-sensitive when consumed incorrectly. Test signals: config loading tests, deprecated-key compatibility tests, service startup tests with default configs, and tests asserting generated default XML keys match these constants.
