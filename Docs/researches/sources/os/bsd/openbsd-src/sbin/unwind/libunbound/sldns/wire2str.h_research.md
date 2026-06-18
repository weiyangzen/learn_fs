# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/wire2str.h

`wire2str.h` declares the sldns wire-to-text conversion interface used by libunbound. It exposes lookup-table globals for algorithms, hashes, CERT algorithms, rcodes, opcodes, EDNS flags/options/EDE codes, wire parse errors, and TSIG errors.

The API is organized in three layers. First are malloc-returning convenience functions for packets, RRs, dnames, type/class names, and rcodes. Second are buffer functions that return the needed character count and silently truncate if the caller buffer is too small. Third are scanner functions that consume `uint8_t**`/length input and advance output `char**`/length pointers as each wire element is parsed.

The header documents scanner behavior in detail: outputs are null-terminated when buffers are supplied, return values are character counts excluding the terminating NUL, input/output pointers are advanced, malformed input may produce shorter diagnostic output, and domain-name scanners optionally use a packet buffer plus compression-loop state.

Declared conversion coverage includes packet headers, full RRs, question RRs, unknown RR/RDATA RFC3597 output, RR comments, types/classes/TTLs, SVCB parameters, all supported RDF field kinds, and EDNS option-specific printers. This header is the contract matched by `wire2str.c`.
