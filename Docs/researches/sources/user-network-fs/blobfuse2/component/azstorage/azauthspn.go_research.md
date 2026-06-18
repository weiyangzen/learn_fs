# sources/user-network-fs/blobfuse2/component/azstorage/azauthspn.go

Purpose: implements service-principal authentication for Blob and ADLS, including client secret, federated token file, and workload identity token assertion flows.

Important APIs/types/functions: `azAuthSPN` embeds `azAuthBase` and `azOAuthBase`; `getTokenCredential` returns an `azcore.TokenCredential`. `azAuthBlobSPN.getServiceClient` and `azAuthDatalakeSPN.getServiceClient` construct storage service clients with that credential.

Control flow: credential selection is branch-based. If `OAuthTokenFilePath` is set, it creates an `azidentity.WorkloadIdentityCredential`. If `WorkloadIdentityToken` is set, it creates a `ClientAssertionCredential` whose callback returns the configured token. Otherwise it creates a `ClientSecretCredential`. Service-client methods then create SDK clients with shared options and propagate/log errors.

State and persistence behavior: client secret or assertion token remains in process memory through `azAuthConfig`; token-file mode reads through Azure Identity. No persistence is performed by this code.

Dependencies/integration: depends on Azure Identity, Azure SDK core, Blob/ADLS service packages, local logging, and client option helpers. It is selected for `SPN` auth mode by `azauth.go`.

Risks: the workload identity token branch creates `ClientAssertionCredentialOptions{}` without passing `clOpts`, unlike the other SPN branches; that may skip custom cloud, authority, resource, or SDK logging options. The callback ignores its context but returns only an in-memory token. Client secret mode needs careful secret handling in config and logs.

Test signals: this file set does not show explicit SPN tests in the visible portion of `azauth_test.go`; the config struct includes SPN fields, so SPN coverage may be elsewhere or absent.
