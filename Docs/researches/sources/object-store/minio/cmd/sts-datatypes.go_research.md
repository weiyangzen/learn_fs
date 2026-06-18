# sources/object-store/minio/cmd/sts-datatypes.go

Purpose: defines XML response models for MinIO's AWS STS-compatible APIs.

Important APIs/types/functions: `AssumedRoleUser`, `AssumeRoleResponse`/`AssumeRoleResult`, `AssumeRoleWithWebIdentityResponse`/`WebIdentityResult`, `AssumeRoleWithClientGrantsResponse`/`ClientGrantsResult`, `AssumeRoleWithLDAPResponse`/`LDAPIdentityResult`, `AssumeRoleWithCertificateResponse`, and `AssumeRoleWithCustomTokenResponse`. Result structs carry temporary `auth.Credentials`, optional assumed-user identity, packed-policy size, provider/audience/subject fields, and request metadata.

Control flow: this file has no executable behavior. Handlers instantiate these structs, set credentials and request IDs, then serialize them through `encodeResponse` and `writeSuccessResponseXML`.

State and persistence behavior: no state is persisted here. The structs define externally visible XML wire contracts for clients and SDKs consuming STS responses.

Dependencies/integration: depends on `encoding/xml` and MinIO `auth.Credentials`. Used exclusively by `sts-handlers.go` success paths.

Risks/test signals: XML names and element names must remain AWS-compatible or clients may fail to parse credentials. Several fields are currently omitted in handler responses despite being modeled. STS integration tests in `sts-handlers_test.go` cover successful credential acquisition and use across LDAP/OpenID flows, but this file has no direct unit tests.
