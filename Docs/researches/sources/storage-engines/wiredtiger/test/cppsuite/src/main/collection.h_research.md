# sources/storage-engines/wiredtiger/test/cppsuite/src/main/collection.h

Purpose: Declares the in-memory representation of one test collection.

Important APIs/types/functions: `collection` stores immutable public `name` and `id`, deletes copy/assignment, and exposes `get_key_count` and `increase_key_count`.

Control flow: documents the required pattern for contiguous key creation: read current count, insert keys at/above it, then increment after successful commit.

State and persistence: private atomic `_key_count` represents modeled row count.

Dependencies/integration: owned by `database` and used by workload operations.

Risks and test signals: model consistency depends on workloads updating key count only after durable commit and coordinating inserts per collection.
