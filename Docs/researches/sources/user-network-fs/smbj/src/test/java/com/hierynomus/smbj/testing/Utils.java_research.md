# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/Utils.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/Utils.java

Purpose: small testing utility for creating `SmbConfig` instances backed by a `StubTransportLayerFactory`. API surface is `config(PacketProcessor)` and `configBuilder(PacketProcessor)`.

State and persistence: no state; returns new builders/configs. Dependencies are `SmbConfig`, `PacketProcessor`, and `StubTransportLayerFactory`. Integration point is Java tests that need a client config with deterministic packet responses. Risks are low; helper changes can affect many tests by altering default transport behavior. Test signal is indirect through callers.
