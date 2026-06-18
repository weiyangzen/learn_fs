# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/extern.h

Declares compatibility syslog entry points.

It forward-declares `struct syslog_data60` and declares `syslog_ss`, `vsyslog_ss`, `syslogp_ss`, and `vsyslogp_ss` with printf-like attributes, plus `__cmsg_alignbytes`.

This is libc compatibility surface for older syslog/control-message ABI.
