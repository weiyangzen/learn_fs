## sources/sync-backup/kopia/fs/ignorefs/ignorefs.go

Purpose: implements an `fs.Directory` wrapper that hides entries matched by Kopia policy ignore rules, dot-ignore files, cache-directory markers, file-size limits, and one-filesystem device constraints.

Important APIs/types/functions: `New`, `Option`, `ReportIgnoredFiles`, `ignoreDirectory`, `ignoreContext`, `ignoreDirIterator`, `parseIgnoreFile`, `resolveSymlink`, `overrideFromPolicy`, and `skipCacheDirectory`. `ignoreDirectory` preserves `fs.Directory` behavior while substituting filtered `Child` and `Iterate` results.

Control flow, state, and persistence: each directory builds or reuses an `ignoreContext` from its parent. Parent ignore decisions are applied first, then local policy and dotfile matchers can negate earlier decisions. Dot-ignore entries can be regular files or symlinks resolved through `resolveSymlink`, capped at 30 hops. The wrapper has no durable persistence; it derives state from policy trees, `.kopiaignore`-style files, and cachedir marker contents during traversal. `sync.Pool` recycles wrapper directories and iterators, so callers must respect `Close`.

Dependencies and integration points: depends on `fs` entry interfaces, `internal/wcmatch` wildcard semantics, `internal/cachedir` signatures, `snapshot/policy` trees, and optional `snapshot.HasDirEntryOrNil`. It integrates into snapshot traversal by making ignored entries appear absent.

Risks and test signals: core risks are rule ordering, negation behavior, symlink loops, accidentally traversing mount points, and pooled-object reuse after close. Tests cover nested policies, symlinked ignore files, negated patterns, one-filesystem filtering, cache directory skipping through behavior, and symlink loop protection.
