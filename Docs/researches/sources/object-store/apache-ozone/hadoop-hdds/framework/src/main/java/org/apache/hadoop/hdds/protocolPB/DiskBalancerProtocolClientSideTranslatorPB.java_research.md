# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolClientSideTranslatorPB.java

## Purpose

This client translator adapts `DiskBalancerProtocol` Java calls to protobuf Hadoop RPCs against a datanode.

## Important APIs, Types, and Functions

The constructor builds `DiskBalancerProtocolPB` via `createDiskBalancerProtocolProxy`. Methods translate `getDiskBalancerInfo`, `startDiskBalancer`, `stopDiskBalancer`, and `updateDiskBalancerConfiguration`. `getUnderlyingProxyObject()` and `close()` expose/stop the proxy.

## Control Flow

Proxy creation sets `ProtobufRpcEngine`, converts `OzoneConfiguration` to Hadoop `Configuration`, and obtains a protocol proxy. Each method builds the appropriate request proto, invokes `rpcProxy`, and converts `ServiceException` to remote `IOException` via `ProtobufHelper`.

## State and Persistence Behavior

State is only the RPC proxy. Persistence is server-side.

## Dependencies and Integration Points

It depends on Hadoop RPC, UGI, NetUtils, disk-balancer protobufs, and the datanode PB interface.

## Risks and Test Signals

`updateDiskBalancerConfiguration` enforces non-null locally; `startDiskBalancer` allows null. Tests should mock the PB proxy for request construction, exception conversion, close behavior, and protocol-engine setup.
