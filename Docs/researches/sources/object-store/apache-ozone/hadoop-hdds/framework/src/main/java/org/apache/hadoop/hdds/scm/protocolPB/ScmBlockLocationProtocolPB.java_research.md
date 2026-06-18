# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ScmBlockLocationProtocolPB.java

## Purpose
`ScmBlockLocationProtocolPB` is the Hadoop RPC protobuf service interface for SCM block-location operations.

## Important APIs, Types, And Functions
It extends `ScmBlockLocationProtocolService.BlockingInterface` generated from protobuf and adds Hadoop annotations: `@ProtocolInfo` with protocol name `org.apache.hadoop.hdds.scm.protocol.ScmBlockLocationProtocol` and version `1`, `@KerberosInfo` using the SCM principal config key, and private interface audience.

## Control Flow
There is no implementation in this file. Hadoop RPC invokes the generated blocking `send` method through implementations and client translators.

## State, Persistence, And Dependencies
The interface holds no state. It depends on generated protobuf service classes, SCM config constants, Hadoop protocol annotations, and Kerberos metadata.

## Integration Points
`ScmBlockLocationProtocolClientSideTranslatorPB` creates retry proxies of this type. Server-side SCM protobuf translators implement the same blocking interface.

## Risks
Changing the protocol name or version is wire-incompatible with Hadoop RPC clients. Annotation drift can break Kerberos principal resolution.

## Test Signals
Compatibility tests should assert protocol name/version and successful RPC proxy construction against an SCM block service.
