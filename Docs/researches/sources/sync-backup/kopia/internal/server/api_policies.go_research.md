# sources/sync-backup/kopia/internal/server/api_policies.go

Purpose: implements policy list/get/resolve/delete/update APIs for snapshot sources.

Important APIs/types/functions: `handlePolicyList`, `getSnapshotSourceFromURL`, `handlePolicyGet`, `handlePolicyResolve`, `handlePolicyDelete`, and `handlePolicyPut`.

Control flow: source identity is parsed from URL query parameters. List returns policy definitions, get fetches direct policy for a source, resolve computes effective policy with inheritance, delete removes direct policy in a write session, and put decodes and stores a policy for the source.

State and persistence behavior: put/delete mutate repository policy manifests; list/get/resolve are read-only.

Dependencies and integration points: integrates `snapshot.SourceInfo`, `snapshot/policy`, server API wrappers, and source manager refresh behavior.

Risks and test signals: URL-derived source identity must preserve host/user/path correctly; policy writes should refresh source scheduling. Tests cover CRUD and effective policy behavior.
