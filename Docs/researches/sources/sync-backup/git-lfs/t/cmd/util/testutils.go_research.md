# sources/sync-backup/git-lfs/t/cmd/util/testutils.go

Purpose: reusable Go utilities for creating and manipulating Git LFS test repositories.

Important APIs/types/functions: `RepoType`, `RepoCreateSettings`, `RepoCallback`, `Repo`, `NewRepo`, `NewBareRepo`, `WrapRepo`, `RunGitCommand`, `FileInput`, `CommitInput`, `CommitOutput`, `Repo.AddCommits`, `Repo.AddRemote`, `PlaceholderDataReader`, and sort helpers `RefsByName`, `WorktreesByName`, `WrappedPointersByOid`, `PointersByOid`.

Control flow: init prepends the checkout `bin` directory to PATH. Repo creation initializes temp Git repos, configures user identity, and constructs Git LFS config/filter/filesystem helpers. `AddCommits` checks out/creates branches, performs merges when requested, writes LFS pointer files and media objects via the clean filter, commits at optional dates/identities, creates annotated tags, and returns commit summaries.

State/persistence behavior: creates temp repos and bare remotes, writes `.git/lfs/objects`, pointer files, commits, tags, and remotes. `Cleanup` removes temp repo/gitdir trees and nested remotes while avoiding deletion from inside the target directory.

Dependencies/integration: used by Go tests and `lfstest-testutils`; depends on Git CLI plus Git LFS config/fs/lfs/git packages.

Risks: global deterministic random source is shared and not locked. `RunGitCommand` shells out without custom env isolation. `Cleanup` uses prefix checks that can be imprecise for similarly prefixed paths.

Test signals: generated repositories with expected commits, parents, tags, LFS pointer OIDs, and deterministic placeholder content.
