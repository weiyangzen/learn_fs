# File Research: sources/virtualization/guestfs-tools/diff/diff.c

## Scope

Implements `virt-diff`, comparing filesystems of two virtual machines or disk sets.

## CLI And Setup

- Uses two libguestfs handles, `g` for the first guest and `g2` for the second.
- Supports first guest `-a`/`-d`, second guest `-A`/`-D`, libvirt URI, format/blocksize, key options, CSV, human-readable, checksum, metadata detail flags, time formatting flags, and verbose/trace/version/help.
- Requires at least one source for each guest and rejects extra arguments.
- Enforces read-only inspector mode and rejects human-readable CSV.
- Mounts and inspects each guest independently before traversal.

## Tree Collection

- `visit_guest` recursively traverses `/` using common `visit`.
- Each entry is copied into an in-memory `tree` as path, `statns`, xattrs, and optional checksum.
- If `--checksum` is set and the entry is a regular file, computes a guestfs checksum.
- Unless enabled by flags, normalizes access time, directory link counts, and directory times to avoid noisy diffs.
- Stores entries in visit order, relying on sorted traversal for merge-style comparison.

## Diff Logic

- `diff_guests` walks both sorted file lists.
- Paths only in the first guest are deleted (`-`); paths only in the second are added (`+`).
- Matching paths compare statns and xattrs; matching regular files may compare checksums or mtime/ctime/size as content-change indicators.
- Content changes emit `=` plus metadata, then in non-CSV mode download both files to a temp directory and run external `diff -u`, omitting the first two diff header lines.
- Metadata-only changes emit old and new rows and a `# changed:` row naming changed fields/xattrs.

## Output

- Outputs file type, octal permissions, size, optional uid/gid, optional times, optional extra stat fields, optional checksum, path, symlink target, and optional xattrs.
- Text mode separates fields with spaces and right-aligns sizes; CSV mode escapes strings/binary fields locally.
- Time output supports formatted local time, raw time_t, seconds relative to now, or days relative to now.
- Device numbers are printed as major:minor.

## Dependencies And Risks

- External `diff` command is required for content display.
- Temporary file paths are created under guestfs tmpdir and cleaned after use.
- Comparisons intentionally ignore `st_dev` and `st_ino` in changed-field reporting.
- Large guests can consume substantial memory because all entries and selected checksums are stored before comparison.
