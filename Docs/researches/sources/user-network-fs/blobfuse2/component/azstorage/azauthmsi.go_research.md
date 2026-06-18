# sources/user-network-fs/blobfuse2/component/azstorage/azauthmsi.go

Purpose: implements managed identity authentication for Blob and ADLS storage clients.

Important APIs/types/functions: `azAuthMSI` embeds `azAuthBase` and `azOAuthBase`; `getTokenCredential` builds `azidentity.ManagedIdentityCredentialOptions` and chooses client ID, resource ID, or object ID when configured. `azAuthBlobMSI.getServiceClient` and `azAuthDatalakeMSI.getServiceClient` build the respective storage clients.

Control flow: credential creation starts with shared OAuth client options. Identity selection priority is `ApplicationID`, then `ResourceID`, then `ObjectID`. If none is provided, the default managed identity is used. Service-client methods get the token credential, build client options, construct SDK clients, and propagate errors.

State and persistence behavior: only config is stored in memory. The actual token lifecycle is managed by Azure Identity and the managed identity endpoint. No persistent state is written.

Dependencies/integration: depends on `azidentity`, `azcore`, Blob/ADLS service packages, and local logging/options helpers. A commented-out Azure CLI fallback for object ID remains but is inactive.

Risks: only one identity selector is honored due to priority order; conflicting config silently picks the first non-empty value. Managed identity failures generally occur when acquiring tokens rather than when the credential object is built, so pipeline validation is important. The custom authority/resource behavior comes from `azOAuthBase`.

Test signals: `azauth_test.go` includes block MSI tests for app/resource/object IDs and ADLS MSI app/resource ID tests, gated by `SkipMsi`.
