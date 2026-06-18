<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_import.go -->
# sources/sync-backup/kopia/cli/command_policy_import.go

Purpose: implements `kopia policy import`, reading a JSON map of target strings to `policy.Policy` values from a file or stdin and applying them to repository policy definitions.

Important APIs/types/functions: `commandPolicyImport`, `setup`, `run`, `deleteOthers`, `json.Decoder`, `DisallowUnknownFields`, `snapshot.ParseSourceInfo`, `policy.SetPolicy`, `policy.ListPolicies`, and `policy.RemovePolicy`.

Control flow: setup registers `--from-file`, `--allow-unknown-fields`, `--delete-other-policies`, and target flags. `run` opens the chosen input, decodes policies with unknown-field rejection by default, optionally computes a target allowlist, parses each imported source string relative to the repository client host/user, imports matching policies, and optionally deletes repository policies not imported.

State/persistence behavior: writes policy blobs through `repo.RepositoryWriter`. `--delete-other-policies` can remove any listed repository policy whose target string is not in the imported set after target filtering.

Dependencies/integration: integrates JSON schema compatibility, source-info parsing, policy storage, stdin/file services, and target filters. Risks/test signals: delete filtering compares target strings from the input, so noncanonical or locally parsed target forms must align with persisted `Target().String()` to avoid unexpected removals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_import.go -->
