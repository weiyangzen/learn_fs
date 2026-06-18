# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/iffib.c

`iffib.c` adds commands and status output for non-default interface and tunnel FIBs. Status queries `SIOCGIFFIB` and `SIOCGTUNFIB`, printing only values different from `RT_DEFAULT_FIB`.

The `fib` and `tunnelfib` setters parse unsigned integer values with `strtoul()`, reject trailing garbage and values above `UINT_MAX`, and apply them with `SIOCSIFFIB` and `SIOCSTUNFIB`.
