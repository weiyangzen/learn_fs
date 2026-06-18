# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/write.c

Writes file data, directory records, dump directories, and descriptor terminators.

`writefiles` recursively copies non-directory source files into the image while computing MD5. If an existing dump entry has the same digest and length, it reuses the old block and rewinds `nextblock`; otherwise it inserts the new content into the dump index. It supports block alignment through global `blocksize`.

`writedirs` writes directory trees bottom-up. `_writedirs` first computes directory record lengths with `dowrite == 0`, reserves blocks, writes dot/dotdot/children records, pads, assigns `block`/`length`, and patches dot/dotdot records using `rewritedot` and `rewritedotdot`. `writedumpdirs` handles the special dump-root/year/day hierarchy, where day roots may already be written.

`Cputplan9` writes Plan 9 system-use metadata. `genputdir` writes one ISO/Joliet directory record, handles block-boundary padding, file flags, dates, names, Plan 9 or Rock Ridge extensions, and length calculations. `Cputisodir` and `Cputjolietdir` specialize it. `Cputendvd` writes the volume descriptor set terminator.

Integration points: central write path called by `dump9660.c`; uses `sysuse.c` for Rock Ridge and `cdrdwr.c` for primitive writes.

Risks and notes: directory record length must stay under 255 bytes, enforced by assertions. Empty files get block zero. If a source changes while being written, length is updated with a warning but content consistency depends on the read that just occurred.
