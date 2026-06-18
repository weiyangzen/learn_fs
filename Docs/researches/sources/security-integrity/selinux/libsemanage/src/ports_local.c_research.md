# sources/security-integrity/selinux/libsemanage/src/ports_local.c

Purpose: local port CRUD wrappers and range-overlap validator.

Important APIs/functions: local modify/delete/query/exists/count/iterate/list wrappers and `semanage_port_validate_local`.

Control flow: CRUD delegates to `semanage_port_dbase_local(handle)`. Validation lists local ports, sorts them with `semanage_port_compare2_qsort`, then scans for the next record with matching protocol. If the next low bound is less than or equal to the current high bound, an overlap error is reported.

State/persistence: local port records persist through the local port database and are flushed during commit. Validation reads and frees listed records.

Risks: assumes sort order groups protocol and ascending low bound; only nearest same-protocol neighbor is checked based on that invariant. Tests should include overlapping same-protocol ranges, adjacent non-overlap, different protocols, empty/singleton lists, and commit rejection behavior.
