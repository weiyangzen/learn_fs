# sources/security-integrity/selinux/libsemanage/src/ibendports_file.c

Purpose: implements text parsing and printing for `ibendportcon` local records.

Important functions: `ibendport_print`, `ibendport_parse`, `SEMANAGE_IBENDPORT_FILE_RTABLE`, `ibendport_file_dbase_init`, and release. The record format is `ibendportcon <ibdev> <port> <context>`.

Control flow: parsing requires the literal header, device name, integer port, and non-`<<none>>` context. It converts context text with `semanage_context_from_string`, sets fields on a caller-created record, and validates trailing parse state. Printing retrieves a newly allocated ibdev name string and context string, emits a single line, then frees both.

State/persistence: used by `dbase_file` for local ibendport stores. It mutates parse target records and writes to a supplied stream. Risks include rejecting `<<none>>`, integer parsing accepting only unsigned-looking values through `parse_fetch_int`, and cleanup correctness on partial parse failure. Tests should cover round-trip, bad headers, invalid contexts, missing fields, and duplicate detection in local validation.
