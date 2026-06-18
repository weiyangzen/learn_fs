# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisResponse.java

Purpose: Converts local SCM method return values and Ratis client replies into a uniform success/result/exception wrapper for HA proxies.

Important APIs and types: `encode(result, type)` serializes non-null results into `SCMRatisResponseProto`; `decode(RaftClientReply)` returns a success wrapper, empty success for empty messages, or failure wrapper for reply exceptions.

Control flow: Encoding resolves the declared return type through `ScmCodecFactory` and writes type name plus serialized bytes. Decoding first checks `reply.isSuccess`; failed replies keep the exception. Successful non-empty responses validate type and value fields, resolve the class, and deserialize the value.

State and persistence behavior: No persistent state; response messages are transient Ratis replies.

Dependencies and integration points: Used by generated invokers, `SCMRatisServerImpl`, and `SCMHAManagerStub` to bridge method return values across Ratis.

Risks and test signals: Void/null results intentionally become `Message.EMPTY`, so callers must not expect a typed null. Tests should cover exception preservation, empty success, primitive wrapper returns, list returns, and invalid response protos with missing fields.
