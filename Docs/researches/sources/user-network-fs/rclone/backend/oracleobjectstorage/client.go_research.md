# sources/user-network-fs/rclone/backend/oracleobjectstorage/client.go

Purpose: builds and configures the OCI Object Storage SDK client, selects authentication providers, wires rclone's HTTP client, and defines retry behavior plus no-auth support for public buckets.

Important APIs: `expandPath` cleans paths and expands leading `~`. `getConfigurationProvider` selects instance principal, user principal, resource principal, workload identity, no-auth, or default config provider based on `Options.Provider`. `newObjectStorageClient` creates `objectstorage.ObjectStorageClient`, applies region/endpoint overrides, and calls `modifyClient`. `modifyClient` installs `fshttp.NewClient(ctx)` and no-auth signer when configured. `shouldRetry` handles context cancellation, OCI `common.ServiceError` request timeouts, generic retryable errors, and HTTP retry status codes. `noAuthConfigurator` and `noAuthSigner` satisfy OCI SDK interfaces with empty credentials and no signing.

Control flow: main `NewFs` calls `newObjectStorageClient`; all backend SDK requests then use the configured client and shared `shouldRetry` inside pacer calls. User principal config warns if the config file path does not exist but still returns a custom profile provider, letting the SDK surface final auth errors.

State and persistence behavior: no persistent state is written. It reads local OCI config files indirectly through SDK providers and may inspect file existence. The client stores HTTP client, signer, host, region, and auth behavior in memory.

Dependencies and integration points: integrates OCI Go SDK `common`, `auth`, and `objectstorage`; rclone `fshttp`, `fs`, and `fserrors`. The no-auth path is used with option provider `no_auth` and is important for public bucket reads where listing all buckets is not allowed.

Risks: `expandPath` assumes paths beginning with `~` have at least two characters and uses `cleanedPath[2:]`, so a bare `~` could be mishandled. No-auth returns empty region and unknown auth type, so endpoint/region configuration must be correct elsewhere. Retry policy combines SDK retries with rclone pacer and intentionally low pacer retry count in the main backend; changing this can multiply retries. Missing config file is logged but not fatal at provider creation.

Test signals: no direct unit tests in this subset. Integration tests exercise client creation for configured providers.
