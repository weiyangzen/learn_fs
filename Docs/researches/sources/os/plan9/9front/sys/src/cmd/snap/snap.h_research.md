# File Research: sources/os/plan9/9front/sys/src/cmd/snap/snap.h

Purpose: Shared data model and prototypes for the `snap` tools.

Key definitions:
- Proc file enum: segment, fd, fpregs, kregs, noteid, ns, proc, regs, status.
- `Pagesize = 1024`, independent of kernel page size.
- `Data`: captured proc-file byte blob.
- `Seg`: memory/text segment with offset, length, page pointers.
- `Page`: deduplicated page data plus serialization reference metadata.
- `Proc`: process snapshot with proc-file data, memory segments, and text segment.

Integration: Included by capture, read, write, snapfs, and utility files.

Risks:
- `debug` is defined in the header, creating a shared global under Plan 9 build assumptions.
- `Data.data[1]` uses variable trailing allocation idiom.
