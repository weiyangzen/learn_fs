# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/conf.h

`conf.h` defines driver/module configuration interfaces and flags. Kernel content declares STREAMS module switch entries, device ops table globals, stream table lookup macros, device attach/detach/probe/quiesce wrappers, non-DDI block/character device call-through helpers, and property/poll/mmap/devmap entry points.

It also defines driver flags for new/old style, tape, MT safety, STREAMS perimeter modes and modifiers, 64-bit offset support, synchronous STREAMS, devmap, hotplug, unsigned 64-bit uio offset, direct transport, interruptible open, and single-instance modules.
