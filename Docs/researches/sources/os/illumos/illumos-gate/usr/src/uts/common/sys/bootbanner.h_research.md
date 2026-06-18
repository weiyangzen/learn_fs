# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootbanner.h

This small header exposes boot-banner rendering for system and zone consoles. It declares `bootbanner_print(void (*)(const char *, uint_t))`, allowing callers to provide an output callback.
