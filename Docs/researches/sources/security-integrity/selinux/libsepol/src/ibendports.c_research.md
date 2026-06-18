# sources/security-integrity/selinux/libsepol/src/ibendports.c

Purpose: adapts high-level InfiniBand end-port records to policydb `OCON_IBENDPORT` object-context linked lists. It supports count, existence, query, modify, and iteration operations over end-port contexts.

Important APIs and functions: public APIs are `sepol_ibendport_count`, `sepol_ibendport_exists`, `sepol_ibendport_query`, `sepol_ibendport_modify`, and `sepol_ibendport_iterate`. Internal converters are `ibendport_from_record` and `ibendport_to_record`.

Control flow: `ibendport_from_record` allocates an `ocontext_t`, allocates/copies the device name, copies the port, converts the high-level context to `context_struct_t`, and stores it in `context[0]`. Query/existence linearly scan `policydb->ocontexts[OCON_IBENDPORT]` for exact device and port. Modify converts the record and prepends it to the list. Iterate converts each low-level entry to a high-level record, invokes a callback, and stops if the callback returns positive.

State and persistence behavior: modifies in-memory policydb ocontext lists only; actual policy serialization is elsewhere. `modify` always prepends and does not replace an existing matching end-port, so duplicate keys can be introduced.

Dependencies and integration points: depends on context conversion (`context_from_record`, `context_to_record`), handle/debug, policydb ocontext layout, and `ibendport_record.c` APIs. Kernel-to-CIL and expand code also understand `OCON_IBENDPORT`.

Risks: lack of duplicate replacement can make query return the most recently prepended match while older duplicates remain. Error cleanup for allocated `u.ibendport.dev_name` is incomplete in some paths because the err block frees the `ocontext_t` but not always nested name storage. Linear scans are acceptable for small policy object lists but can be costly if many entries exist.

Test signals: count/query/exists/iterate on empty and populated lists, modify duplicate behavior, context conversion failures, callback early-stop and failure handling, memory cleanup under allocation failure, and CIL output round trips for `ibendportcon`.
