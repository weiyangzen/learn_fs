# sources/storage-engines/wiredtiger/examples/c/ex_pack.c

Purpose: demonstrates the standalone structure packing and unpacking helpers.

Important APIs and control flow: `main` opens a connection/session, calls `wiredtiger_struct_size(session, &size, "iii", 42, 1000, -9)`, conditionally notes where larger allocation would occur, packs three integers into a fixed buffer with `wiredtiger_struct_pack`, then unpacks them back into `i`, `j`, and `k` with `wiredtiger_struct_unpack`.

State and persistence: only opens a database and session; no table data is created. The packed buffer is stack-local.

Dependencies and integration: depends on the WiredTiger packing format syntax, session context, and `test_util.h`. The example complements raw cursor examples that unpack key/value `WT_ITEM` buffers.

Risks: the fixed buffer is safe only because size is checked before packing; real code must allocate if required. Format strings and C destination types must stay aligned.

Test signals: successful size/pack/unpack calls validate the packing API and integer format handling.
