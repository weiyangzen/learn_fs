# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerClientProtocol.java

Purpose: Client-side extension of `OzoneManagerProtocol` that adds thread-local S3 authentication management needed by the S3 Gateway while it builds OM requests.

Important APIs and types: Methods `setThreadLocalS3Auth`, `getThreadLocalS3Auth`, `clearThreadLocalS3Auth`, and `getS3CredentialsProvider` expose a `ThreadLocal<S3Auth>`.

Control flow: Interface only. Implementations attach S3 auth to each generated OM request, typically in the shared submit path.

State and persistence behavior: No persistence. The intended state is per-thread and per-request; callers must clear credentials after S3 request handling to avoid leakage across reused worker threads.

Dependencies and integration points: Implemented by `OzoneManagerProtocolClientSideTranslatorPB`; consumed by S3 Gateway request handlers and OM protocol clients.

Risks: Thread-local credentials are easy to leak in pools. `getS3CredentialsProvider` exposes the mutable `ThreadLocal`, so callers can bypass setter/clearer conventions.

Test signals: Verify S3 credentials are inserted into requests only for the active thread, are absent after clear, and strict auth-check paths fail when credentials are missing.
