<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/TokenHelper.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/TokenHelper.java

Purpose: datanode-side wrapper for generating block and container tokens when security and token features are enabled.

Important APIs and control flow: the constructor checks block-token and container-token flags from `SecurityConfig`, treats a non-null `SecretKeySignerClient` as security availability, obtains the current short user name, and creates `OzoneBlockTokenSecretManager` and/or `ContainerTokenSecretManager` with the configured expiry. `getBlockToken` grants READ, WRITE, and DELETE modes for a `BlockID` and length when the manager exists. `getContainerToken` creates a container token when enabled. `encode` converts non-null Hadoop tokens to URL strings.

State and persistence: no disk persistence. Runtime state consists of optional token secret managers and the short user name. When security or token modes are disabled, methods return null tokens.

Dependencies and integration: integrates with SCM/datanode security classes, `SecretKeySignerClient`, Hadoop `UserGroupInformation`, `BlockID`, and `ContainerID`. Callers must tolerate null token outputs.

Risks and test signals: tests should cover all combinations of security client present/absent and block/container token flags. Token expiry should follow block token expiry config for both token types. Null returns are intentional but risky for callers that blindly encode or attach tokens.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/TokenHelper.java -->
