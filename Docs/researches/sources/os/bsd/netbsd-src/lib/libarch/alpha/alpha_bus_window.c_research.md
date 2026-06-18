# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_bus_window.c

Alpha bus-window helper library code. `alpha_bus_getwindows()` asks the kernel for a count and then fetches each `alpha_bus_space_translation` with `sysarch`.

`alpha_bus_mapwindow()` opens `/dev/mem`, computes window size from bus range and address shift, maps the physical system window with `mmap`, and stores address/size in the caller’s window object. `alpha_bus_unmapwindow()` releases that mapping with `munmap`.
