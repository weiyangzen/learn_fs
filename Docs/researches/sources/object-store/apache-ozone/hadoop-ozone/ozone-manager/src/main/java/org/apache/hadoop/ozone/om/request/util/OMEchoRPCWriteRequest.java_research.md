
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OMEchoRPCWriteRequest.java

Purpose: Handles write-path EchoRPC requests by returning a generated payload of requested response size without mutating OM metadata.

Important APIs and types: Extends `OMClientRequest`; uses `EchoRPCRequest`, `EchoRPCResponse`, `PayloadUtils.generatePayloadProto2`, `OmResponseUtil`, and `OMEchoRPCWriteResponse`.

Control flow: Validation reads the echo request, generates a protobuf `ByteString` payload sized by `payloadSizeResp`, builds an echo response, wraps it in a standard OM response, and returns it.

State and persistence behavior: No DB/cache mutation. It is a write request only in the sense that it travels through write RPC/Ratis code paths.

Dependencies and integration points: Used for RPC benchmarking/testing and integrates with standard OM response construction.

Risks: Large requested payloads can stress memory/network. Tests should cover payload size accuracy and no metadata side effects.
