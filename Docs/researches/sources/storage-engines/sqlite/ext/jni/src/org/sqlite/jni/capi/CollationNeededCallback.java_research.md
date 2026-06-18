# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CollationNeededCallback.java

## Purpose
Callback interface for lazy collation registration when SQLite encounters an unknown collation.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `void call(sqlite3 db, int eTextRep, String collationName)`.

## Control Flow
SQLite invokes the callback from `sqlite3_collation_needed` handling. Implementations normally call `sqlite3_create_collation` for the requested name.

## State And Persistence Behavior
No intrinsic state. Registration persists on the database handle until replaced or closed.

## Dependencies And Integration Points
Installed via `CApi.sqlite3_collation_needed`, which behaves like SQLite's UTF-16 collation-needed interface because Java strings are UTF-16.

## Risks And Edge Cases
SQLite has no callback error channel here, so exceptions are suppressed. Implementations must avoid recursive failures where the requested collation is never installed.

## Test Signals
Prepare/query SQL using an initially unknown collation and verify callback installation, encoding value, and suppressed exception behavior.
