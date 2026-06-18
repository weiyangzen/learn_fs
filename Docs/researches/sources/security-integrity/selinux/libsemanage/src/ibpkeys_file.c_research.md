# sources/security-integrity/selinux/libsemanage/src/ibpkeys_file.c

Purpose: implements parser/printer support for `ibpkeycon` local records.

Important functions: `ibpkey_print`, `ibpkey_parse`, `SEMANAGE_IBPKEY_FILE_RTABLE`, `ibpkey_file_dbase_init`, and release. Records are printed as `ibpkeycon <subnet_prefix> <pkey|low - high> <context>`.

Control flow: parsing requires header and subnet prefix, then parses either a single integer pkey or a hyphenated range with optional spaces around the hyphen. It rejects `<<none>>` contexts, sets the record range or pkey, and requires clean trailing parse state. Printing emits either a single pkey or range based on low/high equality.

State/persistence: used by `dbase_file` for local ibpkey stores. Dependencies are parse utilities, context conversion, and ibpkey record wrappers.

Risks: range bounds are not validated here for ordering or overlap; that is handled by libsepol setters and local validation. Tests should include compact and spaced ranges, single pkeys, invalid contexts, bad prefixes, malformed hyphens, and round-trip persistence.
