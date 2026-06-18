# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/OMProxyInfo.java

Purpose: Extends Hadoop `ProxyInfo<T>` with OM-specific node identity, RPC address, and delegation-token service metadata.

Important APIs/types/functions: `newInstance` builds an OM proxy record, defaulting null node IDs to `OM_DEFAULT_NODE_ID`. Accessors expose node ID, address string, socket address, token service, and proxy. `createProxyIfNeeded` lazily initializes the proxy with a checked address-to-proxy function. Nested `OrderedMap<P>` provides an immutable ordered list plus node ID to index lookup.

Control flow and state: The outer object is mostly immutable except the inherited proxy reference, which is synchronized for lazy creation. Unresolved RPC addresses log a warning and suppress delegation-token service creation. `OrderedMap` builds a `LinkedHashMap`, rejects duplicate node IDs through Ratis preconditions, and asserts ordering invariants.

State and persistence behavior: No persistence. `dtService` is derived from the resolved RPC socket address and is null for unresolved addresses.

Dependencies and integration points: Used by `OMFailoverProxyProviderBase` to order failover candidates, map leader node IDs to proxies, validate suggested leader addresses, and expose delegation-token service names. Integrates with Hadoop `NetUtils`, `SecurityUtil`, and Ratis precondition helpers.

Risks: Unresolved addresses leave `dtService` null, which can affect token selection. The proxy object is lazily created and wrapped in `IllegalStateException` on creation failure, so callers must treat lookup as potentially failing at first use. `OrderedMap` is immutable only if the input proxy objects are not externally mutated except intended proxy initialization.

Test signals: Tests should verify duplicate node rejection, iteration/index invariants, address/node `contains` matching, unresolved address handling, and lazy proxy creation only once.
