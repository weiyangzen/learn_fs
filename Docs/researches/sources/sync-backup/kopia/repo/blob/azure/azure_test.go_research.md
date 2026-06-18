# sources/sync-backup/kopia/repo/blob/azure/azure_test.go

Purpose: verifies Azure SDK telemetry/user-agent integration.

Important APIs/types/functions: `TestUserAgent`, `blob.ApplicationID`, and Azure client construction paths.

Control flow: the test creates an Azure service/client configuration and asserts Kopia's application ID is present in the configured telemetry/user-agent behavior. It focuses on client options rather than live storage calls.

State and persistence behavior: no Azure blobs are mutated. State is limited to constructed client options.

Dependencies/integration points: protects the integration between Kopia's blob package identity and Azure SDK telemetry. This matters for supportability and provider-side observability. Risks/test gaps include no validation of every credential mode's effective HTTP headers, and no live request inspection. It is a narrow but useful signal that the provider brands its requests as intended.
