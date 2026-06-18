# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CallbackProxy.java

## Purpose
Marker interface and documentation anchor for Java callbacks that proxy SQLite C callbacks.

## Important APIs, Types, And Functions
Defines no methods. Its javadoc states common naming rules and exception-handling expectations for callback interfaces.

## Control Flow
No executable flow. Implementing interfaces define callback-specific `call()` methods invoked from JNI.

## State And Persistence Behavior
No state. Native code may retain instances of implementing callback objects depending on the registration API.

## Dependencies And Integration Points
Implemented by callback interfaces such as busy handler, authorizer, hooks, collation, auto-extension, and prepare multi.

## Risks And Edge Cases
The no-throw convention is documented rather than enforced. Exceptions may be converted only where SQLite has an error reporting path; otherwise they are suppressed.

## Test Signals
Indirect callback tests should verify thrown exceptions do not escape native frames and are translated or suppressed according to each callback contract.
