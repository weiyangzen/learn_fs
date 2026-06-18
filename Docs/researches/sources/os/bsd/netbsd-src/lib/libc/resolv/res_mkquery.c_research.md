# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_mkquery.c

Read completely: 326 lines.

This file constructs DNS query packets. `res_nmkquery` creates QUERY, NS_NOTIFY_OP, and legacy IQUERY messages; with EDNS0 enabled, `res_nopt` appends an OPT pseudo-RR and `res_nopt_rdata` appends OPT option RDATA and updates RDLEN.

Key behavior: query construction zeroes the DNS header, generates a new random ID, sets opcode/RD/AD flags, compresses QNAME with `dn_comp`, writes QTYPE/QCLASS, optionally adds notify completion-domain records, and bounds all writes against the caller buffer. EDNS0 advertises caller answer size capped at 65535 and sets DNSSEC OK when `RES_USE_DNSSEC` is active.

Important interactions: `res_query.c` uses this before `res_nsend`; EDNS NSID/DNSSEC options are driven by resolver state flags.

Security/reliability notes: returns `-1` on short buffers or unsupported opcodes. `res_nopt_rdata` validates the RDATA pointer is within the message, but callers must pass the RDLEN field relationship correctly.
