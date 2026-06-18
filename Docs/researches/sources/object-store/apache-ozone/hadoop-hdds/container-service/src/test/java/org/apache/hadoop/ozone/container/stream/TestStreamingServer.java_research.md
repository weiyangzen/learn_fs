## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/TestStreamingServer.java

Purpose: Integration tests for directory streaming server/client, including plain streaming, SSL streaming, missing stream IDs, timeout handling, and channel cleanup on timeout.

Important APIs/types/functions: `StreamingServer`, `StreamingClient`, `DirectoryServerSource`, `DirectoryServerDestination`, `StreamingException`, Netty `SslContext`, `SelfSignedCertificate`, and `streamDir`.

Control flow: Tests create source/destination subdirectories, write one file, start a server on port 0, stream a subdir through a client, and compare bytes. SSL test builds server/client SSL contexts with a self-signed certificate. Failure test streams a missing ID and expects runtime failure. Timeout tests override `getFilesToStream` to sleep longer than the client timeout and assert an exception, including a no-try-with-resources client path that explicitly closes after checking timeout message.

State and persistence behavior: Uses temporary source and destination directories and writes real file contents.

Dependencies and integration points: Exercises network server startup, client connection, directory source/destination, optional TLS, and timeout/channel lifecycle.

Risks and test signals: Network and timing tests can be environment-sensitive. The channel-leak test documents a previous bug class around `await()` timeout handling.
