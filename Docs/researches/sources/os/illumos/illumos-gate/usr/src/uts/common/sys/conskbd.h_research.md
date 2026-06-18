# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/conskbd.h

`conskbd.h` defines private state for the console keyboard STREAMS aggregation layer. It includes STREAMS, console-device, keyboard, and keyboard-translation dependencies.

The header models lower keyboard queues, queued/pending messages, lower-queue states, ioctl/message tracking, and overall console keyboard state. It is used to multiplex and coordinate keyboard input below the console abstraction.
