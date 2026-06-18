## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HsyncGenerator.java

Purpose: Freon subcommand `hg`/`hsync-generator` that simulates HBase WAL-style writes plus concurrent `hsync` calls on a Hadoop FS file.

Important APIs/types/functions: options configure root path, bytes per write, and writes per transaction. `call` opens a file, starts a daemon transaction writer, and runs `sendHsync` tasks. Shared state includes `writtenTransactions` queue and `lastSyncedTransaction`.

Control flow: initialize Freon, get FS from URI, create `<root>/<object0>`, prepare payload, start writer thread. The writer loops forever, writing `writesPerTransaction` records and enqueueing transaction IDs. Freon worker tasks take transaction IDs and call `outputStream.hsync` only when the transaction is newer than the last synced value.

State and persistence behavior: writes to one persistent file and forces syncs. Local queue and atomic integer coordinate writer/sync threads.

Dependencies and integration points: uses Hadoop `FileSystem`/`FSDataOutputStream`, Ozone payload utilities, and `BaseFreonGenerator`.

Risks: daemon writer runs indefinitely until JVM exit and can throw unchecked exceptions; shared output stream is written and synced by different threads; queue backpressure can block writer; output stream is not protected by explicit synchronization.

Test signals: hsync timer count and generated file existence; stress runs reveal sync latency and concurrency issues.
