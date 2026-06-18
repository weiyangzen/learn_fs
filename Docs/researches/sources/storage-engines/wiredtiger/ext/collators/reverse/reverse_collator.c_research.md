# sources/storage-engines/wiredtiger/ext/collators/reverse/reverse_collator.c

Purpose: implements a loadable collator named `reverse` that orders byte-string keys in reverse lexicographic order.

Important APIs and control flow: `collate_reverse` receives two `WT_ITEM` keys, compares the common prefix with `memcmp`, inverts the comparison result, and reverses length tie-breaks so shorter keys sort after longer keys under the reversed order. A static `WT_COLLATOR reverse_collator` points at this compare function. `wiredtiger_extension_init` registers it via `connection->add_collator(connection, "reverse", &reverse_collator, NULL)`.

State and persistence: no mutable extension state; the static collator lives for process lifetime. Registered collator state is connection-local.

Dependencies and integration: depends on `wiredtiger_ext.h`, module loading convention `wiredtiger_extension_init`, and schemas/indexes configured to use `collator=reverse`.

Risks: the comparator treats keys as raw bytes and is safe for binary data, but reverse ordering must remain strict and transitive. No terminate callback is needed because no allocation occurs.

Test signals: loading the extension and creating/searching an index with `collator=reverse` should show descending byte order.
