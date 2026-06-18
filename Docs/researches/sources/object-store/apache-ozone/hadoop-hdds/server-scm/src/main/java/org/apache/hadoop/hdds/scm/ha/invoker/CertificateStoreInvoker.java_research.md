# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/CertificateStoreInvoker.java

Purpose: Generated non-reflection invoker/proxy for HA replication of `CertificateStore` operations.

Important APIs and types: `ReplicateMethod` covers `removeAllExpiredCertificates` and `storeValidCertificate(BigInteger, X509Certificate, NodeType)`. `newProxy` delegates read/local methods to the implementation and routes selected writes through Ratis.

Control flow: `storeValidCertificate` uses `invokeReplicateClient`, while `removeAllExpiredCertificates` uses `invokeReplicateDirect`. `invokeLocal` switches on method names, casts arguments, calls the underlying store, and encodes non-void results through `SCMRatisResponse`.

State and persistence behavior: The invoker has no own persistence; it replicates mutations against certificate tables in `SCMMetadataStore`.

Dependencies and integration points: Depends on certificate codecs for `BigInteger` and `X509Certificate`, `NodeType` enum codec, and the shared `ScmInvoker` exception translation path.

Risks and test signals: Generated parameter arrays must match overload arity. `storeValidScmCertificate` is local-only here, so callers must understand its HA semantics elsewhere. Tests should cover replicated valid cert storage, expired certificate removal return list, read-only pass-throughs, and method-not-found failure.
