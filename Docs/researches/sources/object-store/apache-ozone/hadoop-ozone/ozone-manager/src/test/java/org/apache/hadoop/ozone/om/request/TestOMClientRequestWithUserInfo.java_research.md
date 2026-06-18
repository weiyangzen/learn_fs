# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestOMClientRequestWithUserInfo.java

Tests how `OMClientRequest` subclasses attach and reconstruct request user information for Hadoop RPC and gRPC/S3 credential transports. Setup uses a mocked `OzoneManager`, real temporary `OmMetadataManagerImpl`, `OMMetrics`, `OzoneConfiguration`, mocked `OmConfig`, and mocked `OMLayoutVersionManager` so request preExecute logic can run without a full OM.

Important APIs include `OMBucketCreateRequest.preExecute`, `OMClientRequest.getUserInfo`, `OMKeyCommitRequest`, `getRemoteAddress`, `createUGI`, and `getHostName`. The Hadoop transport test statically mocks `Server.getRemoteUser`, `Server.getRemoteIp`, and `Server.getRemoteAddress`, then verifies preExecute adds `UserInfo` and that the request can reconstruct the original remote IP, hostname, and Hadoop username. The gRPC/S3 test statically mocks `Context.key("CLIENT_HOSTNAME")` and `Context.key("CLIENT_IP_ADDRESS")`, builds an S3 credential request, and asserts `UserInfo` combines hostname/IP with the S3 access ID.

The file does not validate persisted metadata rows. Its observable state is protobuf request mutation: the original request lacks user info, while the preExecuted request contains it. Integration points are Hadoop IPC static server context, gRPC context keys, S3 credential parsing, bucket create and key commit request classes, and bucket layout handling.

Risks covered are audit/user attribution regressions in transport-specific identity extraction. Gaps include missing remote user/IP, malformed IP, and mixed transport metadata. Test signals are `hasUserInfo`, exact username/host/IP equality, and correct S3 access ID mapping.
