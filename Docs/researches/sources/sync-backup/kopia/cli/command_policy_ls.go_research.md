<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_ls.go -->
# sources/sync-backup/kopia/cli/command_policy_ls.go

Purpose: implements `kopia policy list`/`ls`, showing all defined policies in text or JSON form.

Important APIs/types/functions: `commandPolicyList`, `jsonOutput`, `textOutput`, `jsonList`, `policy.ListPolicies`, and `policy.TargetWithPolicy`.

Control flow: setup wires the command alias, JSON options, text output, and repository-reader action. `run` begins a JSON list wrapper, loads policies, sorts them by target string for deterministic output, and emits either JSON records including ID, target, and policy, or text lines containing policy ID and target.

State/persistence behavior: read-only over repository policy metadata. No policy inheritance is evaluated; the command lists defined policies only.

Dependencies/integration: integrates CLI output abstractions and the policy package's list API. Risks/test signals: text output is intentionally minimal and depends on deterministic `Target().String()` ordering; JSON consumers get one object per policy through the shared JSON list machinery.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_ls.go -->
