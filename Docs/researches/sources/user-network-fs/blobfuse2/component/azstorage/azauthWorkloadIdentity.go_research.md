# sources/user-network-fs/blobfuse2/component/azstorage/azauthWorkloadIdentity.go

Purpose: implements workload identity/client assertion authentication for Blob and ADLS service clients. It exchanges a managed identity token for a client assertion credential, optionally using an on-behalf-of flow.

Important APIs/types/functions: `azAuthWorkloadIdentity` embeds `azAuthBase` and `azOAuthBase`; `getTokenCredential` returns an `azcore.TokenCredential`. `azAuthBlobWorkloadIdentity.getServiceClient` constructs a Blob service client, while `azAuthDatalakeWorkloadIdentity.getServiceClient` constructs an ADLS service client.

Control flow: `getTokenCredential` builds identity client options, creates a managed identity credential using `ApplicationID` as client ID, then defines a callback that requests a token for `api://AzureADTokenExchange` or the configured auth resource. If `UserAssertion` is empty, it creates `ClientAssertionCredential`; otherwise it creates an on-behalf-of credential with client assertions. Service-client methods obtain this credential, build storage service client options, and call the Azure SDK client constructors.

State and persistence behavior: no durable state exists. Tokens are obtained through Azure Identity credential objects and callback flow. Config values remain in memory on the auth object.

Dependencies/integration: depends on Azure SDK `azidentity`, `azcore`, token policy options, Blob service client, ADLS service client, and local logging/client option helpers. It is selected by `azauth.go` when `AuthMode` is workload identity.

Risks: token acquisition uses `context.Background()` inside the client assertion callback rather than the callback's provided context, limiting cancellation propagation. `ApplicationID` is always used as the managed identity client ID; absent or wrong values will fail later during token retrieval. The behavior of `AuthResource` is overloaded as both token exchange scope and cloud service override through the shared OAuth option helper.

Test signals: no dedicated unit test appears in this file set. Integration coverage would require a correctly configured managed identity and workload identity environment, which `azauth_test.go` does not explicitly enumerate.
