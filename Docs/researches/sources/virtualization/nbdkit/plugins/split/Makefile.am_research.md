# File Research: sources/virtualization/nbdkit/plugins/split/Makefile.am

Automake rules for `nbdkit-split-plugin.la`, disabled on Windows because `device_size` support is unavailable there. It builds `split.c` with nbdkit headers, common include/replacement/utils paths, compatibility library, utility library, Windows import hook, module/shared flags, and optional plugin linker script.

The file also distributes POD documentation and conditionally generates `nbdkit-split-plugin.1` with shared magic-parameter text.
