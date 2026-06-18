# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/sysuse.c

Writes Rock Ridge and SUSP system-use fields for directory records.

The core challenge is fitting records into limited system-use space. `Cbuf`, `freespace`, `ensurespace`, and `setcelen` manage continuation areas and CE records. `Cputstring` splits long NM-like strings across records. `Cputsysuse` computes and optionally writes the SUSP/RRIP records for one directory entry: SP and ER records at the root, RR flags, PX POSIX mode/link/user/group metadata, NM alternate names, SL symlink components, and TF timestamps.

Helper writers emit specific records: `CputsuspCE`, `CputsuspER`, `CputsuspRR`, `CputsuspSP`, `Cputrripname`, `CputrripSL`, `CputrripPX`, and `CputrripTF`. `mode` maps Plan 9 mode bits to POSIX file type/mode fields; `nlink` fabricates POSIX link counts.

Integration points: `write.c` calls `Cputsysuse` from `genputdir` when `CDrockridge` is active.

Risks and notes: comments emphasize complexity and several approximations. Symbolic link support depends on `CHLINK`. The `mode` function asserts only directory/regular support even though it has symlink logic, so symlink handling may be build-sensitive. Continuation record logic is assertion-heavy and layout-sensitive.
