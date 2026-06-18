# sources/storage-engines/wiredtiger/ext/collators/revint/revint_collator.c

Purpose: implements a loadable collator named `revint` for integer secondary indexes sorted descending by index key while preserving ascending primary-key ordering among duplicates.

Important APIs and control flow: `REVINT_COLLATOR` embeds `WT_COLLATOR` first and stores `WT_EXTENSION_API`. `revint_compare` unpacks each `WT_ITEM` with extension pack APIs using format `ii`, treating a missing primary key as `INT64_MIN` so a search key without a primary key sorts before duplicate index entries. It then reverses comparison of the first integer and compares primary integers normally. `revint_terminate` frees the allocated collator. `wiredtiger_extension_init` allocates/configures the collator, stores the extension API, registers it as `revint`, and frees on registration failure.

State and persistence: per-extension allocated collator state lasts until WiredTiger calls terminate. No table data is written by the extension itself.

Dependencies and integration: depends on `wiredtiger_ext.h`, extension pack/unpack stream APIs, integer key schemas, and module loading conventions.

Risks: only valid for index keys and primary keys encoded as integers. Error paths must close pack streams correctly; the implementation handles several but depends on API behavior when the second integer is absent. Ordering must remain compatible with search semantics for duplicate keys.

Test signals: extension load, index creation with `collator=revint`, duplicate index-key searches, and cursor iteration order validate behavior and missing-primary-key handling.
