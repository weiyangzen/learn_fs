<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_compression.go -->
# sources/sync-backup/kopia/cli/command_policy_set_compression.go

Purpose: implements content and metadata compression policy flags for `policy set`.

Important APIs/types/functions: `policyCompressionFlags`, `policyMetadataCompressionFlags`, `setCompressionPolicyFromFlags`, `setMetadataCompressionPolicyFromFlags`, `compression.Name`, `compression.ByName`, `applyPolicyNumber64`, and `applyPolicyStringList`.

Control flow: setup registers `--compression`, `--metadata-compression`, min/max compression size strings, and add/remove/clear lists for only-compress and never-compress patterns. Setters apply size changes, map `inherit` to an empty compressor name, set explicit compressor names including `none`, and update sorted pattern lists.

State/persistence behavior: stores compression algorithm names and size thresholds directly in policy. Size thresholds are parsed as raw integer bytes, not human suffixes. Empty algorithm names mean inherited/default, while `"none"` is a concrete disabled value in display logic.

Dependencies/integration: depends on registered compression algorithms from `repo/compression` and on policy evaluation during snapshot upload. Risks/test signals: users may expect size suffix parsing; the CLI currently accepts only integer strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_compression.go -->
