# sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/Security.proto

Purpose: Stable protobuf interface for Hadoop/Ozone security tokens and credential transport.

Important APIs/types/functions: Generates `SecurityProtos` under `org.apache.hadoop.ozone.security.proto`. Defines `TokenProto`, `CredentialsKVProto`, `CredentialsProto`, and delegation-token request/response messages for get, renew, and cancel.

Control flow, state, and persistence: The file serializes security material: token identifiers, passwords, kind, service, credential aliases, and optional secrets. Delegation-token messages flow through OM client protocol and security services. It does not store data directly, but persisted or transmitted credentials must remain compatible.

Dependencies and integration points: Used by `OmClientProtocol.proto` token operations and by Hadoop security/token machinery. Proto package is `hadoop.common`, indicating common security reuse.

Risks: Marked stable, so compatibility requirements are stricter than the OM private protocols. Token bytes and secrets are sensitive; logs and debugging must avoid exposing serialized content. Required token fields make partial token objects invalid.

Test signals: No module-local tests. Downstream security and delegation-token integration tests are the meaningful coverage, along with proto compatibility checks.
