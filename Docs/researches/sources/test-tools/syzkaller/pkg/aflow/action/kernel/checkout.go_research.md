# sources/test-tools/syzkaller/pkg/aflow/action/kernel/checkout.go

## Purpose

`checkout.go` provides cached and scratch Linux kernel checkout actions. It centralizes access to a shared full Linux repo, applies known compatibility fixes/backports, and creates shallow clones for workflow use.

## Important APIs, Types, and Functions

`Checkout` wraps `checkout`, and `CheckoutScratch` wraps `checkoutScratch`. `checkoutArgs` selects `KernelRepo` and `KernelCommit`; `checkoutResult.KernelSrc` is a cached source tree. `checkoutScratchArgs.KernelSrc` produces a temp `KernelScratchSrc`. `kernelBackports` lists commits needed for out-of-tree builds. `UseLinuxRepo` serializes access to the shared repo with `repoMu`. Helpers include `runSandboxedGit` and `shallowGitClone`.

## Control Flow

`checkout` builds a cache key from the requested commit plus backport hashes, enters the shared repo via `UseLinuxRepo`, and populates a cached shallow clone by switching or checking out the commit. It conditionally reverts a known bad compile-commands commit if its revert is absent, applies required backports, commits those backports when applied, and shallow-clones the prepared tree into the cache directory. `checkoutScratch` shallow-clones a cached source tree into a temp dir for edit workflows.

## State and Persistence Behavior

The shared repo lives under `ctx.Workdir/repo/linux` and is protected by a process mutex. Prepared source trees live in aflow cache entries under `src`. Scratch clones live in temp dirs removed by context close.

## Dependencies and Integration Points

It uses syzkaller `vcs`, `osutil`, target constants, and git. All kernel-dependent flows call it before build, code search, reproduction, or patch editing.

## Risks and Edge Cases

The process-local mutex does not coordinate across processes. The shared repo can be left in a transient state if an operation fails before the next checkout repairs it. Backport commits are committed into the shared repo before shallow clone, so user identity is supplied explicitly. `shallowGitClone` assumes the target dir exists and can run `git init`. Network/repo fetch failures propagate as infrastructure errors.

## Test Signals

No direct tests are present in the assigned set. Workflow registration validates dataflow, while integration tests must cover real repo checkout, backport application, bad-commit revert logic, and scratch clone creation.
