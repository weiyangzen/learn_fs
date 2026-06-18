## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClientFactory.java

### Purpose
`OzoneClientFactory` centralizes construction of RPC-based `OzoneClient` instances, HA service-id resolution, token renewal/cancel client routing, and client leak tracking.

### Important APIs and Types
- `track(AutoCloseable)` registers objects with `LeakDetector` and captures stack traces through `HddsUtils`.
- `getRpcClient()` creates a client using a new `OzoneConfiguration`.
- `getRpcClient(String omHost, Integer omRpcPort, MutableConfigurationSource)` validates and writes `ozone.om.address`.
- `getRpcClient(String omServiceId, ConfigurationSource)` creates a HA client only when the service ID is configured.
- `getRpcClient(ConfigurationSource)` selects no service ID, the single configured service ID, or errors when multiple service IDs require caller disambiguation.
- `getOzoneClient(Configuration, Token<OzoneTokenIdentifier>)` decodes a token identifier and routes token renew/cancel clients based on token OM service ID and local HA configuration.
- Private `getClientProtocol` creates `RpcClient` and unwraps `RemoteException` or `IOException` causes.

### Control Flow
Factory methods validate required parameters with `Objects.requireNonNull`, inspect OM service-id settings, and construct `RpcClient` before wrapping it in `OzoneClient`. Token routing handles four key cases: token with default service ID on non-HA/single-node Ratis HA, token service ID matching configured HA, token service ID mismatching configured HA, and old tokens without service IDs. Mismatches produce explicit `IOException`s to avoid renewing against the wrong OM cluster.

### State and Persistence Behavior
The factory has static leak-detector state only. It mutates provided mutable configuration in the host/port overload by setting `OZONE_OM_ADDRESS_KEY`; otherwise it creates clients without persistent local state.

### Dependencies and Integration Points
It depends on `RpcClient`, OM config keys, `OmUtils`, Hadoop `Configuration`, `OzoneConfiguration`, `Token<OzoneTokenIdentifier>`, `RemoteException`, and HDDS leak utilities. It is the canonical entry point for creating `OzoneClient`.

### Risks and Edge Cases
Multiple configured HA service IDs require explicit caller selection; this avoids ambiguity but may break clients expecting fallback. Token renewal for old tokens without service IDs is intentionally rejected in local HA configurations. The host/port overload mutates the caller-provided configuration, so tests and callers should account for side effects. Error unwrapping preserves remote IO causes but wraps other exceptions in a generic message.

### Test Signals
Tests should cover service-id selection, multiple-service-id errors, host/port config mutation, token routing for default/matching/mismatched/no-service-id tokens, `RpcClient` exception unwrapping, and leak tracking registration.
