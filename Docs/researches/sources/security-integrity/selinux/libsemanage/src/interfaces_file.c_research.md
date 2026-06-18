# sources/security-integrity/selinux/libsemanage/src/interfaces_file.c

Purpose: text backend for local network-interface `netifcon` records.

Important functions: `iface_print`, `iface_parse`, `SEMANAGE_IFACE_FILE_RTABLE`, `iface_file_dbase_init`, and release. Format is `netifcon <name> <ifcon> <msgcon>`.

Control flow: parser verifies the header, reads interface name, parses and rejects NULL/`<<none>>` interface and message contexts, sets both contexts, and requires valid trailing parse state. Printer converts both contexts to strings and emits one line.

State/persistence: local interface state is read/written through `dbase_file`. Dependencies include parse utilities, context conversion, interface record wrappers, and `database_file`.

Risks: both contexts are mandatory; partial setter failure must free the temporary context. Tests should cover valid round-trip, invalid header, missing message context, `<<none>>`, invalid context string, and whitespace/comment handling.
