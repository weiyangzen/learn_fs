# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifclone.c

`ifclone.c` implements clone-interface creation/destruction commands and the `-C` cloner listing option. It uses `libifconfig` to list cloners and `SIOCIFDESTROY`/`SIOCIFCREATE2` for default create/destroy behavior.

The file maintains a list of default creation callbacks matched by interface-name prefix or custom filter. `ifclonecreate()` picks a matching callback when a clone type needs parameterized creation, otherwise it performs a bare create. It special-cases `ipfw`/`ipfwlog` names with a warning that explicit creation is unnecessary in FreeBSD 16.0.

Registered commands are clone-only `create`/`plumb` and normal `destroy`/`unplumb`.
