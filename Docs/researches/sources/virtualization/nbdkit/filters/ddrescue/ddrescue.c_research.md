# File Research: sources/virtualization/nbdkit/filters/ddrescue/ddrescue.c

Purpose: restricts readable ranges according to GNU ddrescue mapfile status.

Key details:
- Parses `ddrescue-mapfile`.
- Skips comments and first status line, then parses tab-separated offset, length, and status.
- Stores only `+` ranges as readable ranges.
- Rejects negative offsets/lengths.
- Disables write and cache support.
- `.pread` succeeds only if the entire requested range is contained inside one recorded good range; otherwise returns `EIO`.

Risk notes:
- Reads spanning adjacent good ranges are rejected unless contained in a single stored range.
- No range merging or sorting is performed.
