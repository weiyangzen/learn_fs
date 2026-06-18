# sources/sync-backup/kopia/cli/command_acl_add.go

## Purpose
Implementation of `acl add`, which creates repository ACL entries for a user, target manifest selector, and supported access level, with optional overwrite semantics.

## APIs, Types, and Functions
Important APIs include types `commandACLAdd`; functions/methods `setup`, `run`; Kingpin command(s) add: Add ACL entry; flags user: User the ACL targets, target: Manifests targeted by the rule (type:T,key1:value1,...,keyN:valueN), access: Access the user gets to subject, overwrite: Overwrite existing rule with the same user and target.

## Control Flow, State, and Persistence
Control flow registers command(s) add: Add ACL entry, binds flags user: User the ACL targets, target: Manifests targeted by the rule (type:T,key1:value1,...,keyN:valueN), access: Access the user gets to subject, overwrite: Overwrite existing rule with the same user and target, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata, ACL manifests and access-rule entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strings, github.com/pkg/errors, github.com/kopia/kopia/internal/acl, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/acl, kopia/repo plus external packages context, strings, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
