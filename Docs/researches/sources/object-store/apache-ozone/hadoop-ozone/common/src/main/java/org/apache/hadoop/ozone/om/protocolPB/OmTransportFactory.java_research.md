# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OmTransportFactory.java

Purpose: Factory SPI for constructing OM client transports. It allows a transport implementation to be discovered by `ServiceLoader` or loaded from OM transport class configuration.

Important APIs and types: Instance method `createOmTransport(ConfigurationSource, UserGroupInformation, String)` and static methods `create` and `createFactory`. It uses `OZONE_OM_TRANSPORT_CLASS` and `OZONE_OM_TRANSPORT_CLASS_DEFAULT`.

Control flow: `create` delegates to `createFactory`, then calls the instance factory method. `createFactory` first checks `ServiceLoader<OmTransportFactory>` and returns the first implementation found. If none exists, it loads the configured class from this interface's class loader and instantiates it via `newInstance`. Any error is wrapped in `IOException`.

State and persistence behavior: No persistent state. Runtime choice can vary by classpath service entries or configuration.

Dependencies and integration points: Integrates Java SPI, Ozone configuration, UGI, OM service IDs, and client translator construction. This is the extension point for switching Hadoop RPC/gRPC/custom transports.

Risks: First service-loader result wins, which can be surprising when multiple providers are present. Reflective `newInstance` requires a public no-arg constructor and wraps details. Classpath order can alter transport behavior.

Test signals: Cover SPI discovery precedence, configured-class fallback, failure wrapping for bad classes, and correct propagation of conf/UGI/service ID into created transport.
