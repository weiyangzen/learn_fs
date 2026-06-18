<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate10.py

Purpose: verifies follower fast truncate operates over the logical union of stable and ingest data, independent of which physical component contains a key.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin`, `concat`, `range_inclusive`, and scenarios for `layered:fast_truncate` plus `table:fast_truncate`. Shared helpers create stable data with `setup_leader`, follower ingest data with `setup_follower`, apply `truncate`, and enumerate `visible_keys`.

Control flow: tests cover empty stable/ingest, ranges that hit no keys, ranges that cover only stable keys, only ingest keys, disjoint stable/ingest keys, overlapping stable/ingest keys, and partial overlap across both tables. Each test computes the exact expected logical key list after truncate.

State and persistence behavior: stable keys come from leader checkpoint state; ingest keys are follower-local writes. Truncate must treat the layered view as one sorted table and hide every key in the specified range regardless of component.

Dependencies/integration points: checks integration between stable table cursor, ingest table cursor, range delete bookkeeping, and table-layered configuration. Risks are duplicate/overlap resolution bugs where one component leaks a key hidden in the other. Test signals are exact visible-key arrays.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate10.py -->
