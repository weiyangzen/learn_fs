# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifstf.c

`ifstf.c` implements 6rd/STF tunnel configuration support. It registers `stfv4net` and `stfv4br`, plus an `af_stf` status callback.

All driver communication goes through `do_cmd()`, which wraps `SIOCSDRVSPEC`/`SIOCGDRVSPEC` with `struct ifdrv`. Status fetches `STF6RD_GV4NET` and prints IPv4 prefix plus border relay address.

`setstf_br()` parses an IPv4 border relay address and sends `STF6RD_SBR`. `setstf_set()` parses `address/prefixlen`, validates prefix length 1-32 using `strtonum()`, parses the IPv4 address, and sends `STF6RD_SV4NET`.

Notable behavior: `setstf_set()` temporarily writes a NUL over the slash in the argument string, restores it only on one error path, and otherwise exits or completes without restoring. This is typical old ifconfig-style parsing but assumes mutable command argument storage.
