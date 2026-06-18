# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgre.c

`ifgre.c` adds GRE tunnel key, UDP port, and option handling. Status prints a nonzero GRE key, optional UDP encapsulation port, and option bits for checksum, sequence, and UDP encapsulation.

Commands set `grekey` with `GRESKEY`, set `udpport` with `GRESPORT`, and toggle `enable_csum`, `enable_seq`, and `udpencap` by reading `GREGOPTS`, changing bits, and writing `GRESOPTS`.
