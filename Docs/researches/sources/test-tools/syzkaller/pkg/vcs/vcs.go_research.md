# sources/test-tools/syzkaller/pkg/vcs/vcs.go

## Purpose

`vcs.go` defines the public VCS abstraction, shared commit/recipient/bisection types, repository factory functions, patch application, validation predicates, release-tag parsing, and web link generation.

## Important APIs, Types, And Functions

`Repo`, `Bisecter`, and `ConfigMinimizer` define repository capabilities. Data types include `Commit`, `CommitShort`, `RecipientInfo`, `Recipients`, `BisectResult`, `BisectEnv`, and `RepoOpt`. Constructors include `NewRepo`, `NewSyzkallerRepo`, and `NewLKMLRepo`. Utilities include `Patch`, `CheckRepoAddress`, `CheckBranch`, `CheckCommitHash`, `ParseReleaseTag`, `CanonicalizeCommit`, and `CommitLink`/`TreeLink`/`LogLink`/`FileLink`.

## Control Flow, State, Dependencies, And Integration

The file mostly contains pure helpers, except `Patch` and `runSandboxed`, which shell out under sandboxing and mutate the target directory. `NewRepo` selects Linux, Fuchsia, generic Git, or TestOS implementations based on target OS and VM type. Link generation normalizes GitHub SSH URLs and handles GitHub, kernel.org, cgit, and googlesource formats.

## Risks And Test Signals

Regex validators are approximate and may accept/reject edge-case repository addresses or branch names. `Patch` first dry-runs, checks reverse application to detect already-applied patches, then applies for real; sandbox correctness is security-sensitive. `vcs_test.go` covers patch safety, validators, canonicalization, link formats, and Linux maintainer parsing.
