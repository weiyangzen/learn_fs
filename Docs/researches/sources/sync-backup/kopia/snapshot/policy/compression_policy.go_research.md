# sources/sync-backup/kopia/snapshot/policy/compression_policy.go

Purpose: defines file and metadata compression policy and file-level compressor selection.

Important APIs/types/functions: `CompressionPolicy` includes compressor name, only/never extension lists, no-parent flags, and min/max size thresholds. `MetadataCompressionPolicy` stores metadata compressor. Definition structs track source fields. Methods include `CompressorForFile`, `CompressionPolicy.Merge`, `MetadataCompressionPolicy.Merge`, and `MetadataCompressor`.

Control flow: `CompressorForFile` returns no compressor for `"none"`, below min, above max, or extension in `NeverCompress`. If `OnlyCompress` is non-empty and the extension is present, it returns the configured compressor; otherwise it falls through to the configured compressor. Merge helpers fill scalar values and union extension lists unless no-parent flags prevent future parent merges.

State and persistence behavior: policy persists as JSON in manifests. The chosen compressor affects object writer options and persisted object/content compression metadata.

Dependencies/integration: depends on `fs.Entry`, `repo/compression.Name`, and policy merge helpers.

Risks: `OnlyCompress` semantics as implemented do not restrict compression to only listed extensions; if a file extension is not in `OnlyCompress`, the function still returns the compressor unless blocked by `NeverCompress` or size. That behavior may be intentional or a policy bug. Extension lists must be sorted for `sort.SearchStrings`; merge sorts unioned lists, but user-provided lists used directly by `CompressorForFile` need ordering.

Test signals: no direct tests in this subset; compression behavior is indirectly visible in object/repository tests and policy merge tests.
