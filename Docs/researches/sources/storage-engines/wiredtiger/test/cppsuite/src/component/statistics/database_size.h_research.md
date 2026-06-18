# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/database_size.h

Purpose: Declares the database-size statistic specialization.

Important APIs/types/functions: `database_size` inherits `statistics`, overrides `check` and `get_value`, and has private helpers for database size and file-name enumeration.

Control flow: metrics monitor invokes it as a `statistics` object, but it ignores the passed stats cursor.

State and persistence: stores a reference to the in-memory database model and reads persisted WT files.

Dependencies/integration: includes configuration, database, scoped cursor, and statistics base.

Risks and test signals: database reference lifetime must exceed the statistic object; file layout assumptions should be revisited for new storage modes.
