## sources/user-network-fs/gcsfuse/internal/storage/storageutil/unsupported_path_util.go

Purpose: Detects GCS object names/prefixes that are valid in GCS but unsupported by gcsfuse path semantics.

Important APIs/types/functions: unsupported substring/prefix/suffix/name lists and `IsUnsupportedPath(name string) bool`.

Control flow: returns true for `//`, `/../`, `/./`, leading slash, suffix `/.` or `/..`, and exact empty, `.`, or `..`; otherwise false.

State and persistence behavior: read-only package-level slices.

Dependencies and integration points: used by storage/listing or path validation layers to filter object names that cannot map cleanly to filesystem paths.

Risks: path rules are exact string checks, not normalization. Changes affect visible object filtering and may be user-facing.

Test signals: `unsupported_path_util_test.go` covers supported normal paths and unsupported empty/root/dot/double-slash/path traversal forms.
