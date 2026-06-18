# sources/sync-backup/kopia/cli/command_acl_enable.go

## Purpose
Implementation of ACL enable/reset, creating or resetting ACL policy manifests and bootstrap entries for the authenticated user.

## APIs, Types, and Functions
Important APIs include types `commandACLEnable`; functions/methods `setup`, `run`; Kingpin command(s) enable: Enable ACLs and install default entries; flags reset: Reset all ACLs to default.

## Control Flow, State, and Persistence
Control flow registers command(s) enable: Enable ACLs and install default entries, binds flags reset: Reset all ACLs to default, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata, ACL manifests and access-rule entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/internal/acl, github.com/kopia/kopia/internal/auth, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/acl, kopia/internal/auth, kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
