# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocolPB/DiskBalancerProtocolServerSideTranslatorPB.java

## Purpose

This server translator adapts protobuf DiskBalancer RPCs to a local `DiskBalancerProtocol` implementation.

## Important APIs, Types, and Functions

It implements `DiskBalancerProtocolPB`, stores `impl`, and implements protobuf service methods for info, start, stop, and update configuration.

## Control Flow

Each RPC unwraps request fields, calls `impl`, builds an empty or data-bearing response, and wraps `IOException` in `ServiceException`. `startDiskBalancer` maps absent config to `null`.

## State and Persistence Behavior

Only the delegate reference is stored. Mutations and persistence happen in the datanode implementation.

## Dependencies and Integration Points

It is registered on datanode RPC servers and pairs with the client translator.

## Risks and Test Signals

`updateDiskBalancerConfiguration` calls `request.getConfig()` without checking presence, relying on proto defaults. Tests should cover absent/present config behavior, exception wrapping, and response info preservation.
