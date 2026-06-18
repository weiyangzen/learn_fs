# sources/user-network-fs/blobfuse2/component/azstorage/azauth.go

Purpose: defines the common authentication configuration and factory for Azure Storage connections. It chooses the correct auth implementation for Blob or ADLS accounts and centralizes Azure Identity client option construction.

Important APIs/types/functions: `azAuthConfig` carries account name/type, protocol, auth mode, key/SAS/MSI/SPN/workload identity fields, OAuth resource and authority overrides, and endpoint. `azAuth` is the interface implemented by each auth mode with `getEndpoint`, `setOption`, and `getServiceClient`. `getAzAuth`, `getAzBlobAuth`, and `getAzDatalakeAuth` dispatch by account type and auth mode. `azAuthBase` supplies default endpoint and no-op option behavior. `azOAuthBase.getAzIdentityClientOptions` builds `azcore.ClientOptions`.

Control flow: storage setup calls `getAzAuth` with parsed config. The factory logs account details, selects Blob or ADLS, then returns a concrete key, SAS, MSI, SPN, Azure CLI, or workload identity wrapper. Unsupported auth modes log critical errors and return nil. OAuth option creation starts from cloud configuration for the storage endpoint, adds SDK logging, and optionally overrides Active Directory authority host and resource manager endpoint.

State and persistence behavior: auth config is copied into each concrete auth object. SAS auth can later update its in-memory `SASKey` through `setOption`; other modes ignore dynamic options by default. No credentials are persisted here.

Dependencies/integration: depends on Azure SDK `azcore` and `cloud`, local logging, account/auth enum helpers, cloud configuration and SDK log helpers defined elsewhere in azstorage. Concrete auth implementations in sibling files satisfy the `azAuth` interface.

Risks: a nil return from the factory is the main failure signal and must be checked by storage setup. The OAuth resource override mutates `cloud.ResourceManager`, which is used as the service scope in the SDK options; correctness depends on the rest of the SDK expecting this shape for storage auth. Config contains many credential fields in memory, so logging must avoid printing secrets; this file logs account and endpoint only.

Test signals: `azauth_test.go` exercises invalid auth/account cases and each major auth mode at integration level through `NewAzStorageConnection`, `SetupPipeline`, and `TestPipeline`, but relies on external Azure credentials.
