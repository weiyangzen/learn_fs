# sources/user-network-fs/blobfuse2/component/azstorage/azauthsas.go

Purpose: implements SAS-token authentication for Blob and ADLS service clients.

Important APIs/types/functions: `azAuthSAS` embeds `azAuthBase`, overrides `setOption` for `saskey`, and overrides `getEndpoint` to append the SAS token to the configured endpoint. `azAuthBlobSAS.getServiceClient` and `azAuthDatalakeSAS.getServiceClient` create no-credential SDK service clients.

Control flow: service-client creation rejects empty SAS keys, builds the relevant storage SDK client options, then calls `NewClientWithNoCredential` with the endpoint plus normalized SAS query. `strings.TrimLeft(..., "?")` allows either raw or question-mark-prefixed SAS values. Dynamic SAS refresh flows through `setOption` and later service-client recreation.

State and persistence behavior: SAS token is stored in memory in `azAuthConfig`. No token is written to disk. `getEndpoint` constructs a full URL containing the token each time it is called.

Dependencies/integration: depends on Blob and ADLS service client packages, logging, strings, and client option helpers. `BlockBlob.UpdateServiceClient` uses this auth mode's `setOption` to refresh SAS credentials.

Risks: SAS-bearing endpoints include secret query parameters. Logging code must avoid printing full SAS endpoints; this file logs only failures and not the full constructed endpoint. Empty SAS fails early, but expired or insufficient SAS permissions fail during pipeline validation or operations.

Test signals: `azauth_test.go` covers empty SAS failures, account/container SAS success paths, HTTP container SAS, ADLS SAS, and dynamic SAS update through `UpdateServiceClient`.
