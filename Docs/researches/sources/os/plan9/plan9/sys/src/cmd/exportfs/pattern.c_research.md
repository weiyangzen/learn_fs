# File Research: sources/os/plan9/plan9/sys/src/cmd/exportfs/pattern.c

Adds include/exclude pattern support for exported directory reads. Patterns are loaded from `patternfile` into regular-expression arrays.

Key behavior:
- `exclusions()` reads lines beginning with `+ ` or `- ` and compiles them with Plan 9 regexp support.
- Include patterns are treated as required matches: if a path fails any include regexp, it is excluded.
- Exclude patterns remove paths that match.
- `preaddir()` wraps directory reads to filter entries and maintain directory offsets in the `Fid` structure.

Important implementation details:
- Directory offset handling is intentionally strict: offset zero rewinds the cached directory buffer, while any non-current offset fails.
- `preaddir()` keeps an un-emitted entry in the cache if `convD2M()` reports insufficient output space.
- Paths are converted through `makepath(f->f, d->name)` before filtering, and root is normalized to `/`.

Risks and invariants:
- `excludefile()` assumes `include` and `exclude` are initialized when filtering is enabled.
- Filtering can make directory offsets synthetic because skipped entries do not advance the returned byte count.
