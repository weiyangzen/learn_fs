# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/cec.c

This module decodes a small CEC protocol header containing type, connection, sequence, and length, then prints optional following text.

It supports filters for type, connection, sequence, and length. `p_seprint` maps type values to names such as `Tinita`, `Tdata`, `Tack`, `Tdiscover`, and prints the text payload up to the declared length.

Notable detail: `p_filter` uses assignment instead of comparison for `conn`, `seq`, and `len`, so those filter cases modify the packet header and return the assigned value rather than performing equality tests.
