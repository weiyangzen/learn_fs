<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_group_req.c -->
# sources/test-tools/strace/src/print_group_req.c

Purpose: mpers-aware printer for `struct group_req` socket multicast options.

Important APIs/types/functions: `print_group_req`, `struct_group_req`, `PRINT_FIELD_IFINDEX`, and `PRINT_FIELD_SOCKADDR`.

Control flow: if caller-provided length is shorter than the structure, prints the address; otherwise fetches and prints interface index plus group sockaddr.

State and persistence behavior: no state.

Dependencies and integration points: used by socket option decoders; depends on `<netinet/in.h>`, mpers definitions, interface-index printing, and sockaddr printing.

Risks: structure layout is personality-sensitive. Short lengths intentionally do not attempt partial decoding.

Test signals: native and compat `group_req`, short length fallback, invalid pointer, IPv4/IPv6 multicast sockaddrs, and interface-name rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_group_req.c -->
