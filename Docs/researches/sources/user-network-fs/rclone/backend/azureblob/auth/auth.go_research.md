# Research: sources/user-network-fs/rclone/backend/azureblob/auth/auth.go

## Purpose
This package centralizes authentication and Azure SDK client construction for rclone's Azure storage backends. It defines common config options and a generic `NewClient` factory used by both Blob and Files backends, abstracting over SDK client option types and shared-key credential types.

## Important APIs, Types, and Functions
- `ConfigOptions` declares shared rclone config keys: account/key, SAS URL, connection string, service principal credentials, certificate auth, username/password, environment auth, managed identity, Azure CLI auth, emulator, and endpoint override.
- `Options` is the parsed config struct embedded by Azure backend options.
- `servicePrincipalCredentials` and `parseServicePrincipalCredentials` load `az ad sp create-for-rbac` JSON containing `appId`, `password`, and `tenant`.
- `transporter`, `newTransporter`, and `Do` wrap rclone's `fshttp.NewTransport` as an Azure `policy.Transporter`, adding an APN/rclone user agent via context config.
- `NewClientOpts[Client, ClientOptions, SharedKeyCredential]` is the generic adapter layer that supplies Azure SDK constructors and a callback to inject `policy.ClientOptions`.
- `NewClientResult` returns the constructed SDK client, optional token credential, booleans for shared-key/anonymous auth, and the container parsed from a container-level SAS.
- `NewClient` selects exactly one authentication path and builds the SDK service client.

## Control Flow
`NewClient` first builds Azure policy client options with rclone's transport, then lets the backend copy those into the concrete SDK options. Authentication is selected by a priority-ordered `switch`: environment/default Azure credential, emulator, account/key, SAS URL, connection string, client secret, client certificate, username/password, service principal file, managed identity, workload identity, Azure CLI, or anonymous account-only access. SAS URLs are parsed to distinguish account-level SAS from blob container-level SAS; for container SAS, the endpoint is rewritten without the container path and the result records the constrained container. If a client was not already built by SAS or connection string, `NewClient` derives `https://<account>.<defaultBaseURL>` unless an endpoint override exists, then instantiates the concrete SDK client with shared key, token credential, or no credential.

## State and Persistence
The file persists no remote state itself. It mutates the passed `Options` in limited cases by filling account/key/endpoint defaults for environment or emulator auth and by resolving endpoint from account. Credentials are passed in memory to Azure SDK constructors. The filesystem side effect is reading certificate files or service-principal JSON files after shell expansion.

## Dependencies and Integration Points
It depends on `azcore`, `policy`, `azidentity`, and blob SAS parsing from Azure SDK; rclone config, obscure password reveal, environment expansion, and HTTP transport utilities; and backend-provided constructors. `azureblob.NewFs` and `azurefiles.newFsFromOptions` supply the concrete `NewClientOpts`.

## Risks and Edge Cases
- Auth selection is priority based; conflicting config values silently prefer earlier branches, except MSI identity ID conflicts are explicitly rejected.
- `ClientCertificatePassword` handling appears to reveal `opt.Password` rather than `opt.ClientCertificatePassword`, which risks certificate auth failure when a separate certificate password is configured.
- MSI object ID is declared in config but explicitly unsupported in the current branch.
- Workload identity branch is ordered after `UseMSI`, so configs with both `UseMSI` and workload fields will take the MSI branch.
- Container-level SAS validation applies only when `conf.Blob` is true; Azure Files treats SAS differently through the generic no-credential client path.
- Anonymous auth requires `account` and depends on public endpoint access; missing endpoint with missing account fails.

## Test Signals
There is no direct test file for `auth.go` in this group. Azure Files has a skipped `InternalTestAuth` matrix that would exercise connection string, account/key, and SAS URL via `newFsFromOptions`, but credentials are intentionally blank. Azure Blob and Files integration tests indirectly validate working client construction for configured remotes.
