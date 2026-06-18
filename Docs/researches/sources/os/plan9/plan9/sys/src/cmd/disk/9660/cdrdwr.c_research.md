# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/cdrdwr.c

Core ISO image read/write abstraction for the 9660 toolset.

`createcd` creates a new image, initializes paired read/write `Biobuf`s, writes the 16-sector lead-in, primary volume descriptor, optional El Torito and Joliet descriptors, terminator, optional dump block, boot catalog, and flags. `opencd` opens an existing image, validates length and primary descriptor, infers flags from the system identifier, probes Joliet and dump support, and prepares the same `Cdimg` abstraction.

`big`, `little`, `Cputnl`, `Cputnm`, and `Cputn` handle endian conversions. `Creadblock`, `Cread`, `Cgetc`, `Crdline`, and seek/offset helpers coordinate read buffering with write flushes. `Cputc`, `Cwrite`, `Cputs`, `Cputr*`, `Crepeat`, and `Cpadblock` write structured data and maintain `nextblock`. `Cputdate` and `Cputdate1` write ISO directory and volume timestamps.

`parsedir` converts an on-disc ISO/Joliet directory record into `Direc`, including Plan 9 system-use fields when present. `setroot`, `setvolsize`, and `setpathtable` patch descriptor fields after directory and path table locations are known. `readisodesc` and `readjolietdesc` parse primary/secondary descriptors into `Voldesc`.

Integration points: nearly every 9660 module uses this file’s `Cdimg` I/O and patching APIs.

Risks and notes: asserts enforce many layout invariants. Primary descriptor flag inference uses lowercase string matching after `isostring`. Plan 9 system-use parsing is partial; Rock Ridge parsing is noted as a BUG.
