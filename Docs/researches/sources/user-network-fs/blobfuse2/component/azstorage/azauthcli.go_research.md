# sources/user-network-fs/blobfuse2/component/azstorage/azauthcli.go

Purpose: implements Azure CLI authentication for Blob and ADLS service clients using Azure Identity's CLI credential.

Important APIs/types/functions: `azAuthCLI` embeds `azAuthBase` and provides `getTokenCredential`, which calls `azidentity.NewAzureCLICredential(nil)`. `azAuthBlobCLI.getServiceClient` and `azAuthDatalakeCLI.getServiceClient` create Blob and ADLS service clients respectively.

Control flow: service-client creation gets a CLI token credential, builds storage SDK client options through shared helpers, then calls `service.NewClient` for Blob or `serviceBfs.NewClient` for ADLS. Errors from credential or option construction are logged and returned immediately; client creation errors are logged and returned.

State and persistence behavior: the auth object stores only config. Authentication state is external to the process in the user's Azure CLI login/cache. No token or credential data is persisted by this code.

Dependencies/integration: depends on `azidentity`, `azcore`, Blob and ADLS service packages, and local logging/options helpers. It is selected by the central auth factory for `AZCLI` auth mode.

Risks: runtime behavior depends on the `az` CLI being installed, authenticated, and authorized for the storage account. `NewAzureCLICredential(nil)` does not receive the custom cloud/client options used by MSI/SPN flows, so sovereign cloud or custom authority behavior may differ from other OAuth modes.

Test signals: `azauth_test.go` includes block and ADLS Azure CLI tests that expect `TestPipeline` errors when `SkipAzCLI` is true and success otherwise.
