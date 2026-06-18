# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingException.java

Purpose: unchecked exception type for the custom streaming package.

Important APIs and functions: constructors wrap an `InterruptedException`, wrap a message plus `IOException`, or carry a message string.

Control flow and state: no state beyond `RuntimeException` fields. Callers convert checked IO/interruption conditions into this unchecked type at API boundaries.

Dependencies and integration: thrown by `DirectoryServerSource`, `StreamingClient`, and `StreamingServer`.

Risks and test signals: because it is unchecked, callers must know which streaming operations may fail at runtime. Tests should verify cause propagation, interrupted status restoration by callers, and message content for timeout and incomplete-stream cases.
