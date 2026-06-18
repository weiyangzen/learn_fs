# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/fs.h

Public filesystem/file interface header for fossil modules outside the low-level storage core.

It declares opaque `Fs`, `File`, and `DirEntryEnum` types, open modes, global filesystem-name variables, and APIs for opening/closing/syncing/halt/snapshot/vac, directory enumeration, file creation/walking/read/write/stat/wstat/remove/truncate/clri, qid-space management, and metadata queries.

This is the higher-level boundary above `dat.h`/`fns.h`.
