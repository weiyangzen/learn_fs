# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/jchar.c

Joliet/UCS-2 name handling and secondary volume descriptor writer.

`jolietstring` decodes big-endian UCS-2 bytes to Plan 9 UTF strings and interns them. `isjolietfrog` and `isbadjoliet` enforce Joliet name limits: at most 64 runes and no `*`, `/`, `:`, `;`, `?`, or backslash. `jolietcmp` compares base and extension portions as rune sequences, matching the big-endian encoded ordering.

`Cputjolietsvd` writes a Joliet secondary volume descriptor with UCS-2 fixed strings, escape sequence `%/C`, placeholder root/path/size fields, metadata strings, dates, and file structure version.

Integration points: used by descriptor parsing, name validation/sorting, and optional Joliet tree writing.

Risks and notes: buffers in `jolietcmp` are fixed at 256 runes with a BUG comment. UCS-2 handling does not address surrogate pairs.
