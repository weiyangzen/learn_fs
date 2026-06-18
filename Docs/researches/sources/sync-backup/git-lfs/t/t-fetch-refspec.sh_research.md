# sources/sync-backup/git-lfs/t/t-fetch-refspec.sh

## Purpose

Exercises how `git lfs fetch` resolves explicit refs, tracked branch refs, push-remote configuration, and bad refs. It is a focused contract around selecting the correct remote ref for object discovery.

## Important APIs, control flow, and dependencies

The tests create remotes and clones, track and commit `.dat` files, push to named refs, configure branch upstream or push remote settings, run `git lfs fetch` with explicit or implicit ref arguments, and verify downloaded objects. Bad-ref cases expect a nonzero command and diagnostic output.

## State, dependencies, integration points, risks, and test signals

State includes local branch config, remote refs, object cache contents, and remote object store. Integration points are Git ref resolution, upstream/pushRemote selection, remote name validation, and LFS batch downloads. Risks include fetching from `main` when the tracked ref is different, ignoring `--remote`, or reporting ambiguous ref errors poorly. Signals are local object assertions for good refs and exact greps for invalid ref diagnostics.
