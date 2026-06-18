# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ConfigLogCallback.java

## Purpose
Callback interface for SQLite global `SQLITE_CONFIG_LOG` logging.

## Important APIs, Types, And Functions
Declares `void call(int errCode, String msg)`.

## Control Flow
After installation via `CApi.sqlite3_config(ConfigLogCallback)`, SQLite invokes the callback for global log events.

## State And Persistence Behavior
No interface state. The installed callback is global SQLite configuration state, not per database.

## Dependencies And Integration Points
Used by `CApi.sqlite3_config(ConfigLogCallback)` and native `sqlite3_config(SQLITE_CONFIG_LOG, ...)`.

## Risks And Edge Cases
`sqlite3_config` must not race other SQLite API calls. Logging callbacks should avoid calling back into unsafe SQLite operations or throwing.

## Test Signals
Install/clear logging callback before initialization-sensitive operations, trigger known log events, and verify message/error code delivery.
