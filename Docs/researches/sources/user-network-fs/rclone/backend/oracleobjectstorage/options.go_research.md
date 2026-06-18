# sources/user-network-fs/rclone/backend/oracleobjectstorage/options.go

Purpose: defines Oracle Object Storage backend constants, authentication provider identifiers/help text, the `Options` configuration struct, and the full option registration list consumed by backend `init`.

Important APIs: constants define copy/upload limits and defaults: `maxSizeForCopy`, `maxUploadParts`, `defaultUploadConcurrency`, `minChunkSize`, `defaultUploadCutoff`, `maxUploadCutoff`, `minSleep`, and `defaultCopyTimeoutDuration`. Provider constants cover user principal, instance principal, resource principal, workload identity, environment auth, and no auth. `Options` contains provider, compartment, namespace, region, endpoint, encoding, OCI config file/profile, upload/copy cutoffs, multipart concurrency and limits, checksum behavior, storage tier, resume/cleanup flags, bucket checking, and SSE/BYOK fields. `newOptions` returns `[]fs.Option` with help, defaults, advanced flags, examples, and provider restrictions.

Control flow integration: main backend registration calls `newOptions`. `NewFs`, `client.go`, `multipart.go`, `object.go`, `copy.go`, and `byok.go` consume these fields to configure auth, client endpoint, bucket operations, upload strategy, copy behavior, metadata/checksum handling, storage tier, multipart cleanup/resume, and encryption headers. Test files use setters in the main backend to mutate chunk/cutoff options.

State and persistence behavior: options are parsed from rclone config into `Options`. Sensitive values include namespace, compartment, and SSE material. Runtime code may mutate SSE checksum/algorithm fields after validation. Options directly influence remote persistent state such as bucket creation, object storage tier, object metadata checksums, and encryption mode.

Dependencies and integration points: uses rclone `fs`, `config`, and `encoder`. The default encoder encodes invalid UTF-8, slash, and dot to keep OCI keys compatible with rclone's path model and SDK limitations.

Risks: option bounds are enforced outside this file, so new options must be paired with validation in backend construction/setters. The default `chunk_size` help text describes 5 MiB and `minChunkSize`, consistent with OCI minimum part size. `environmentAuth` is presented as default, but `getConfigurationProvider` falls through to the SDK default provider rather than explicitly handling that constant. SSE options are mutually exclusive in `byok.go`; registration help must stay aligned with that validation.

Test signals: Oracle integration tests expose setters for chunk size, upload cutoff, and copy cutoff; no tests directly validate option metadata/help text or all provider modes.
