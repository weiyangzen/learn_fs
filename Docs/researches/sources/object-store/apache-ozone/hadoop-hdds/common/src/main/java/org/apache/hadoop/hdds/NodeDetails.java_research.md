## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/NodeDetails.java

Purpose: abstract base for HA service node metadata: service ID, node ID, RPC host/port, Ratis port, and HTTP/HTTPS endpoints.

Important APIs: constructors accept either an `InetSocketAddress` or host/port pieces; getters expose service/node IDs, RPC address, resolved/host status, Ratis host:port, HTTP/HTTPS addresses, and a thread name prefix derived from `HddsUtils.threadNamePrefix`.

Control flow: `getRpcAddress()` lazily builds and caches an `InetSocketAddress` from host and RPC port when not supplied. `isHostUnresolved`, `getInetAddress`, and `getHostName` delegate to that address.

State/persistence: mutable fields are initialized in constructors, but no setters are present here. `rpcAddress` is lazily cached and not synchronized. Dependencies: Hadoop `NetUtils`, Java networking, `HddsUtils`.

Integration points: HA node descriptors for SCM/OM style services and thread naming. Risks: lazy cache can preserve stale host/port if subclasses mutate inherited fields indirectly; unresolved addresses can propagate to callers; `getHostName()` may perform reverse lookup depending on `InetSocketAddress`. Test signals: constructor equivalence, unresolved host behavior, Ratis host:port formatting, and thread prefix for null/empty node IDs.
