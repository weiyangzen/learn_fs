# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestDirectoryDeletingService.java

Purpose: Tests FSO directory deletion service behavior, configured concurrency, live reconfiguration, and Ratis request batching. Important APIs and types include `DirectoryDeletingService`, `DirDeletingTask`, `OmTestManagers`, `KeyManager`, `OzoneManagerProtocol`, `OMRequestTestUtils`, FSO `OmDirectoryInfo`/`OmKeyInfo`, `ThreadPoolExecutor`, and `PurgeDirectoriesRequest`.

Control flow: The size-limit test creates one FSO directory and 2000 child files with long names, recursively deletes the directory through the write client, and waits for moved-file counters. The multithread test verifies the deletion executor core size, submits latch-blocked tasks to prove parallelism, then exercises `processDeletedDirsForStore`. `testUpdateAndRestart` applies new thread-count and interval config. The batching test spies `submitRequest`, feeds many large purge paths, and asserts multiple bounded `PurgeDirectories` requests.

State and persistence behavior: Tests write real OM metadata tables for FSO directories/files, deleted-directory state, and service counters. Integration points include recursive delete request handling, OM Ratis byte limits, key manager service wiring, and executor lifecycle.

Risks: Background waits and executor counts are timing-sensitive. Batching assertions depend on protobuf serialized sizes. Test signals are moved-file/run counters, exact thread pool sizing, restarted interval, captured request count, command type, and payload bytes under the configured limit.
