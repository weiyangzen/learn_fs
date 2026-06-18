# sources/security-integrity/selinux/libsemanage/src/ports_file.c

Purpose: text backend for local `portcon` records.

Important functions: `port_print`, `port_parse`, `SEMANAGE_PORT_FILE_RTABLE`, `port_file_dbase_init`, and release. Format is `portcon <tcp|udp|dccp|sctp> <port|low - high> <context>`.

Control flow: parser validates header and protocol, parses a single port or hyphenated range with special spacing rules, rejects `<<none>>` contexts, sets context, and requires valid trailing parse state. Printer emits the protocol string, single/range numeric field, and context string.

State/persistence: used by `dbase_file` for local port stores. Dependencies include parse utilities, port record wrappers, context conversion, and database file backend.

Risks: overlap is not checked here; malformed spacing around ranges can change parse outcome; negative ports are rejected by integer parsing. Tests should cover all protocols, single/range forms, invalid context, invalid protocol, malformed ranges, comments/blanks, and round-trip output.
