# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euctw.c

Read completely: 430 lines.

This module implements EUC-TW ctype and stdenc support for ASCII and CNS-11643 planes. It uses fixed byte-class rules with no module variables.

Key behavior: ASCII is 1 byte, CNS plane 1 is two high-bit bytes, and planes 2 through 7 are four bytes using SS2 followed by a plane selector `0xA2-0xA7` and two high-bit bytes. Wide characters carry a plane marker in the high byte (`'G'` through `'M'`). Standard-encoding csid is the high-byte plane marker and index is the lower 7-bit row/column value.

Important interactions: exports through ctype/stdenc templates.

Security/reliability notes: output conversion validates buffer size before writing. Input conversion resets state on illegal sequences. One notable quirk is the `restart` path in `mbrtowc_priv`, which sets `*nresult = (size_t)-1` while returning 0, unlike the usual `(size_t)-2` incomplete marker used by most other restartable modules.
