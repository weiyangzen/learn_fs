# sources/sync-backup/kopia/cli/command_acl_delete.go

## Purpose
Implementation of `acl delete`, which removes selected ACL entries by ID or all entries, with dry-run output unless the destructive `--delete` flag is supplied.

## APIs, Types, and Functions
Important APIs include types `commandACLDelete`; functions/methods `setup`, `dryRunDelete`, `shouldRemoveACLEntry`, `run`; Kingpin command(s) delete: Delete ACL entry; flags all: Remove all ACL entries, delete: Really delete; arguments id: Entry ID.

## Control Flow, State, and Persistence
Control flow registers command(s) delete: Delete ACL entry, binds flags all: Remove all ACL entries, delete: Really delete, accepts arguments id: Entry ID, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata, ACL manifests and access-rule entries. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/internal/acl, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/acl, kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
