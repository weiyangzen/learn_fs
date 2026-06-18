# sources/user-network-fs/blobfuse2/component/azstorage/azauthkey.go

Purpose: implements shared-key authentication for Blob and ADLS storage accounts.

Important APIs/types/functions: `azAuthKey` embeds `azAuthBase`. `azAuthBlobKey.getServiceClient` validates `AccountKey`, creates an `azblob.SharedKeyCredential`, builds Blob service client options, and constructs a Blob service client. `azAuthDatalakeKey.getServiceClient` mirrors this with `azdatalake.NewSharedKeyCredential` and the ADLS service client.

Control flow: empty shared keys fail fast with a logged error and explicit error value. Invalid key material fails during SDK credential construction. Valid credentials are paired with shared storage client options and used to create service clients for the configured endpoint.

State and persistence behavior: account key is held in memory in `azAuthConfig`. No key material is written by this code. Service clients retain SDK credential state after construction.

Dependencies/integration: depends on Azure SDK Blob and ADLS shared-key credential constructors, service client packages, local logging, and client option helpers. It is selected by `azauth.go` for `KEY` auth mode.

Risks: shared keys are high-value secrets kept in process memory. The implementation guards against empty keys but not accidental logging elsewhere. Invalid base64 or malformed keys are surfaced from SDK constructors. Consumers must ensure HTTPS unless explicitly configured otherwise.

Test signals: `azauth_test.go` covers empty block/adls keys, malformed block key, and positive shared-key auth for block and ADLS accounts.
