# sources/storage-engines/leveldb/include/leveldb/comparator.h

Purpose: declares the key ordering interface used by DBs and tables, plus the built-in bytewise comparator.

Important APIs and types: abstract `Comparator`, `Compare`, `Name`, `FindShortestSeparator`, `FindShortSuccessor`, and `BytewiseComparator`.

Control flow: DB and table code compare user keys through this interface and persist the comparator name in MANIFEST records. Table builders may call separator/successor hooks to shorten index keys.

State and persistence behavior: comparator ordering is part of the persistent database contract. Opening a DB with a comparator name/order mismatch can make stored tables unreadable or incorrectly ordered.

Dependencies and integration: used by `Options`, `InternalKeyComparator`, bloom-filter compatibility guidance, table building, version metadata, and recovery comparator checks.

Risks and edge cases: comparator implementations must be thread-safe and must change `Name()` whenever ordering semantics change. Incorrect separator/successor logic can violate sorted table invariants.

Test signals: bytewise and custom comparators are covered elsewhere; version recovery validates persisted comparator name.
