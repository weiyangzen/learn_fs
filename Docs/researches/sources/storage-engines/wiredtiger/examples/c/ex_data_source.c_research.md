# sources/storage-engines/wiredtiger/examples/c/ex_data_source.c

Purpose: demonstrates how to register a custom `WT_DATA_SOURCE` and implement the data-source/cursor callback surfaces used by WiredTiger extensions.

Important APIs and control flow: `my_data_source_init` stores the `WT_EXTENSION_API`. Data source callbacks (`my_create`, `my_drop`, `my_open_cursor`, `my_rename`, `my_truncate`, `my_checkpoint`, etc.) mostly return success but illustrate extension calls. `my_create` demonstrates error/message printing, Windows error mapping, scratch allocation/free, and strerror. `MY_CURSOR` embeds `WT_CURSOR` first, and `my_open_cursor` allocates it, populates cursor method pointers, reads extension config values, resolves collator config, demonstrates metadata insert/remove/search/update, and returns the cursor. `main` registers `my_dsrc` under `dsrc:` and adds custom method configuration entries of boolean, int, string, and list types with validation.

State and persistence: registers an in-process data source and method configuration on the connection. Metadata examples mutate WiredTiger metadata records, though the demo sequence removes/searches/updates an illustrative key.

Dependencies and integration: depends on `wiredtiger_ext.h`, `WT_EXTENSION_API`, and the extension ABI requirement that public interface structs be the first field in custom structs.

Risks: many callbacks are stubs and not a durable data source. `my_open_cursor` may leak allocated cursor memory if later snippet calls fail. Metadata search after removal is demonstrative and would fail in real flow without surrounding state.

Test signals: compile/link coverage of all callback signatures and successful `add_data_source`/`configure_method` calls.
