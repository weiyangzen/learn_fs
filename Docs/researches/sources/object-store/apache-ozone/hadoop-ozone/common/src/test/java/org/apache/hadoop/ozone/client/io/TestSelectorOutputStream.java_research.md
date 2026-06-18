# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/io/TestSelectorOutputStream.java

Purpose: tests `SelectorOutputStream`, which delays selecting one of two output streams until write volume crosses a threshold.

Important APIs/types/functions: exercises `write`, `flush`, `close`, `hflush`, and `hsync` on `SelectorOutputStream`. The test defines an `Op` enum to dispatch operations and a `SyncableOutputStreamForTesting` implementing Hadoop `Syncable`.

Control flow and state: `runTestSelector` uses memoized suppliers for below-threshold and above-threshold streams. Writes select the above-threshold stream immediately only when bytes written exceed the threshold; below-threshold selection is delayed until a terminal or flush operation needs it.

Dependencies and integration points: depends on Ratis `MemoizedSupplier` and checked functional interfaces, Hadoop `Syncable`, and Java `ByteArrayOutputStream`. It represents client write-path selection between small-object and large-object stream implementations.

Risks and test signals: catches premature stream creation, off-by-one threshold mistakes, and illegal hflush/hsync on non-`Syncable` delegates. Threshold cases at 2, 10, and 20 bytes for threshold 10 check below, exact, and above behavior.
