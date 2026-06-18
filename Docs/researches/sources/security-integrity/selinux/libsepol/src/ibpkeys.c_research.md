# sources/security-integrity/selinux/libsepol/src/ibpkeys.c

Purpose: adapts high-level InfiniBand pkey records to policydb `OCON_IBPKEY` object-context lists, supporting count, existence, query, modify, and iteration.

Important APIs and functions: public APIs are `sepol_ibpkey_count`, `sepol_ibpkey_exists`, `sepol_ibpkey_query`, `sepol_ibpkey_modify`, and `sepol_ibpkey_iterate`. Internal converters `ibpkey_from_record` and `ibpkey_to_record` bridge `sepol_ibpkey_t` and `ocontext_t`.

Control flow: conversion from record allocates an `ocontext_t`, copies subnet prefix bytes and low/high range, rejects low > high, converts the high-level context into `context[0]`, and returns the low-level node. Existence/query scan the `OCON_IBPKEY` list for exact prefix and range. Modify prepends the converted node. Iterate converts each node to a high-level record, calls the callback, frees the temporary record, and stops on positive callback status.

State and persistence behavior: mutates the in-memory policydb ocontext list only. Modify does not replace existing matching entries, so duplicate pkey ranges can remain. Persistence to binary or CIL is handled by other modules.

Dependencies and integration points: depends on `context_from_record`, `context_to_record`, public/internal pkey APIs, policydb ocontext layout, and debug logging. `expand.c` copies `OCON_IBPKEY`, and `kernel_to_cil.c` emits `ibpkeycon`.

Risks: duplicate entries are possible. Error paths include an unused `subnet_prefix_buf` and must destroy partially initialized contexts. Exact matching does not check overlapping ranges, so policy-level conflict validation must happen elsewhere. Endianness of stored subnet prefixes must align with record conversion and CIL output.

Test signals: empty/non-empty count, exact query/exists, duplicate modify behavior, low > high rejection, callback early-stop/failure, subnet prefix round trip through CIL, overlapping range policy validation elsewhere, and allocation-failure cleanup.
