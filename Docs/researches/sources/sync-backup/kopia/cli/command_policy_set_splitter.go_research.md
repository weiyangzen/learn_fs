<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_splitter.go -->
# sources/sync-backup/kopia/cli/command_policy_set_splitter.go

Purpose: implements `policy set --splitter`, overriding the object splitter algorithm for a policy target.

Important APIs/types/functions: `policySplitterFlags`, `setSplitterPolicyFromFlags`, `supportedSplitterAlgorithms`, `splitter.SupportedAlgorithms`, and `policy.SplitterPolicy`.

Control flow: setup registers an enum containing `inherit` and all supported splitter algorithms. The setter leaves empty values unchanged, clears `p.Algorithm` for `inherit`, or stores the explicit algorithm string and increments the change count.

State/persistence behavior: splitter override is a string in the policy. Empty string means inherited/repository default; explicit values override object chunking for affected snapshots.

Dependencies/integration: depends on the splitter registry and policy evaluation during content upload. Risks/test signals: changing splitters affects deduplication boundaries for future snapshots, so policy changes can have storage-efficiency implications even though this layer only stores a string.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_splitter.go -->
