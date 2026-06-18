# sources/sync-backup/git-lfs/t/t-fetch-paths.sh

## Purpose

Validates fetch include/exclude path filters when patterns are directory-like and may be "unclean" or slash-terminated. It ensures config and CLI filters agree for a tracked file in `dir/a.dat`.

## Important APIs, control flow, and dependencies

The setup creates a remote repo with `dir/a.dat`, tracks `*.dat`, pushes the object, and clones a reusable working repo. Subsequent tests remove `.git/lfs/objects`, set `lfs.fetchinclude` or `lfs.fetchexclude`, or pass `-I=dir/` and `-X=dir/`, then run `git lfs fetch`.

## State, dependencies, integration points, risks, and test signals

State includes one remote object, one clone, and mutable per-repo filter config. Integration points are path normalization, include/exclude config loading, CLI filter override parsing, and local object cache writes. Risks include treating `dir/` as an invalid glob, failing to normalize path separators, or leaking previous filter config between tests. Signals are local object presence for include paths and absence for exclude paths.
