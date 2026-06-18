# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/pack.c

Packet marshaling/unmarshaling library for CIFS. Provides byte/memory appenders, little/big-endian integer writers/readers, NetBIOS name packing, SMB path/string packing with Unicode support, ASCII-only packing, and DOS/NT time conversions.

Unpacking functions bound reads by `p->eop` and handle Unicode string termination quirks. `gconv` and `goff` resolve RAP/SMB offset-based strings relative to transaction data or a base pointer. This file is heavily used by all SMB command builders and parsers.
