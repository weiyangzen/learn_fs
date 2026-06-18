# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestOmTransportFactory.java

Purpose: tests discovery and configuration selection for `OmTransportFactory`.

Important APIs/types/functions: exercises `OmTransportFactory.createFactory`, Java `ServiceLoader.load`, `OZONE_OM_TRANSPORT_CLASS`, `OZONE_OM_TRANSPORT_CLASS_DEFAULT`, and factory method `createOmTransport`.

Control flow and state: one test mocks `ServiceLoader` to return a dummy implementation and verifies it is selected. Another mocks an empty loader, verifies the configured default class is used, verifies a configured concrete class name instantiates, and verifies a nonexistent class name throws `IOException`.

Dependencies and integration points: uses Mockito static mocking, `OzoneConfiguration`, `ConfigurationSource`, and `UserGroupInformation`. This factory determines whether OM clients use Hadoop RPC, gRPC, or plugin transports.

Risks and test signals: protects extension discovery, default transport fallback, and config error reporting. A regression here can prevent clients from constructing any OM transport.
