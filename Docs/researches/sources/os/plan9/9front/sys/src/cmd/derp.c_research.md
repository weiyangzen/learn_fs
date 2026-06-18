# File Research: sources/os/plan9/9front/sys/src/cmd/derp.c

Purpose: Three-way directory/file difference classifier, likely for replica-style synchronization planning.

Key behavior:
- Compares local (`myfile`), ancestor (`oldfile`), and remote (`yourfile`) paths.
- Options control quiet/continue-on-error, user checks, time checks, dump qid optimization, size-only behavior, and permission mask.
- `statdir()` obtains a `Dir` and stores the full path in `name`.
- `samefile()` compares Plan 9 qid identity and, for dump directories, can treat equal atime as unchanged subtree.
- `dcmp()` compares dirs/files by qid, type, permissions, users, size, time, or full file content via `cmpfile()`.
- `diffdir()` reads and sorts directories, then merge-walks child names from local/remote/ancestor and recurses.
- `diffgen()` classifies add/delete/modify conflicts and emits two-letter operation codes with optional `!` conflict marker.
- `diff3()` sets up the three initial `Dir` structures and resolves cases where ancestor equals local or remote.

Output examples:
- `an`: local added, remote unchanged/nonexistent.
- `na`: remote added.
- `mn`/`nm`: local or remote modified.
- `dn`/`nd`: local or remote deleted.
- `mm!`, `aa!`, `md!`, `dm!`: conflicts.

Notable details:
- It handles directory/file type changes specially by decomposing into delete/add where possible.
- `-L` disables size checks, forcing content comparison unless time/other checks settle it.
