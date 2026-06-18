# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OmTransport.java

Purpose: Transport abstraction used by the OM client-side translator to submit already-built `OMRequest` messages and receive `OMResponse` messages without hard-coding Hadoop RPC or gRPC.

Important APIs and types: Defines `submitRequest(OMRequest)`, `getDelegationTokenService()`, and `close()`. The token service is returned as Hadoop `Text`.

Control flow: Interface only. Implementations decide serialization, retry/failover, channel lifecycle, and delegation-token service address formatting.

State and persistence behavior: No state in the interface. Implementations generally own RPC channels, failover counters, and service-address metadata; server-side OM owns persistent request effects.

Dependencies and integration points: Consumed by `OzoneManagerProtocolClientSideTranslatorPB` and produced by `OmTransportFactory`. Implementations include Hadoop RPC and gRPC transport classes elsewhere in the package.

Risks: All client protocol behavior flows through this narrow contract. Implementations must preserve request ordering, exception semantics, token service compatibility, and close behavior expected by the translator.

Test signals: Mock transports should verify request construction in translator tests. Transport implementation tests should assert response propagation, IO exception behavior, token service text, and idempotent cleanup.
