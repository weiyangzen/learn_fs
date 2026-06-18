# sources/sync-backup/kopia/cli/command_acl_list.go

## Purpose
Implementation of `acl list`, which reads ACL manifest entries and displays entry IDs, users, targets, and access levels.

## APIs, Types, and Functions
Important APIs include types `commandACLList`, `aclListItem`; functions/methods `setup`, `run`; Kingpin command(s) list: List ACL entries.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List ACL entries, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata, ACL manifests and access-rule entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/internal/acl, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/manifest. It integrates with Kopia repository internals such as kopia/internal/acl, kopia/repo, kopia/repo/manifest plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
