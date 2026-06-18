# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/UpgradeUtils.java

Purpose: small helper for creating datanode layout-version protobuf messages.

Important APIs and functions: `defaultLayoutVersionProto` sets both metadata and software layout versions to `HDDSLayoutVersionManager.maxLayoutVersion()`. `toLayoutVersionProto(int mLv, int sLv)` builds a proto with explicit metadata and software layout versions.

Control flow and state: stateless final utility class with private constructor.

Dependencies and integration: used in protocol registration/version exchange and finalize-new-layout commands where datanodes and SCM communicate layout versions.

Risks and test signals: risk is low, but incorrect defaults can affect upgrade negotiation. Tests should verify max-version defaulting, explicit version fields, and compatibility with `StorageContainerDatanodeProtocolProtos.LayoutVersionProto`.
