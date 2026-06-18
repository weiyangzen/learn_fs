# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/dat.h

Purpose: shared 9660srv data model.

Key behavior: defines sector/name constants; cache structs `Iobuf`/`Ioclust`; underlying device `Xdata`; filesystem operation table `Xfsub`; mounted filesystem `Xfs`; fid state `Xfile`; fid operation modes; and exported error/config globals.

Integration notes: bridges the generic 9P server in `main.c`, cache in `iobuf.c`, fid/device lifetime in `xfile.c`, and ISO implementation in `9660srv.c`.
