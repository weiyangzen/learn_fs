# sources/storage-engines/wiredtiger/examples/c/ex_extending.c

Purpose: demonstrates registering custom collators directly with a WiredTiger connection.

Important APIs and control flow: defines a case-insensitive `WT_COLLATOR` using `strcasecmp`, and a `PREFIX_COLLATOR` struct that embeds `WT_COLLATOR` first plus a `maxlen` configuration field. `__compare_prefixes` casts the base collator pointer back to `PREFIX_COLLATOR` and compares only the first `maxlen` bytes. `main` opens a connection, registers `nocase` and `prefix10`, opens a session, leaves room for application work, and closes.

State and persistence: registers collators for the connection lifetime. No table data is created by the visible example.

Dependencies and integration: depends on the collator ABI and the "interface first" embedding convention. Uses `test_util.h` and platform availability of `strcasecmp`.

Risks: string comparators assume keys are C strings; they are not safe for arbitrary binary `WT_ITEM` keys with embedded NUL bytes. Prefix comparison can intentionally collapse distinct keys over the configured prefix, which has schema consequences.

Test signals: successful `add_collator` calls compile and run. Real validation would create indexed tables using the collators and verify ordering/search semantics.
