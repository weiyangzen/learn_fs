# File Research: sources/os/plan9/9front/sys/src/cmd/rio/dat.h

Central data header for `rio`. Defines qid constants, control message types, window/fid/xfid/filesystem/timer structures, globals, and window operation prototypes.

`Window` combines frame state, images, mouse/keyboard/control channels, text buffer, scroll state, selection, process info, cursor state, labels, and working directory.

The qid layout encodes window id and file id in one path, supporting `/dev` and `/dev/wsys/<id>` file views.
