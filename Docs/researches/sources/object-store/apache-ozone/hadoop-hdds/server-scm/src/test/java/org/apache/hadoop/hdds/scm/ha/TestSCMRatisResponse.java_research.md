<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisResponse.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisResponse.java

Purpose: This suite tests `SCMRatisResponse` decoding from Ratis client replies and response encoding validation.

Important APIs and types: It uses `SCMRatisResponse.decode`, `SCMRatisResponse.encode`, `RaftClientReply`, `RaftGroupMemberId`, `RaftPeerId`, `RaftGroupId`, `ClientId`, `Message`, `LeaderNotReadyException`, `RaftException`, `SCMRatisProtocol.SCMRatisResponseProto`, and `InvalidProtocolBufferException`.

Control flow: Setup creates a reusable raft member ID. The success test decodes a successful reply with `Message.EMPTY` and verifies the result can be encoded back as an object response. The failure reply test decodes a `LeaderNotReadyException` and verifies response success is false, exception is a `RaftException`, and result is null. Additional tests reject encoding a non-protobuf `Message` object and decoding response protos missing type or value.

State and persistence behavior: There is no persistence. State is the Ratis reply metadata, success flag, exception, and serialized response payload.

Dependencies and integration points: This protects the client-side response handling path for SCM Ratis requests, including preserving Raft exceptions and validating proto3 required-equivalent fields.

Risks: Missing-field handling must remain strict to avoid treating malformed replicated responses as valid null/default values.

Test signals: Success flag/result checks, exception type preservation, non-protobuf encode failure, and missing type/value exception messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisResponse.java -->
