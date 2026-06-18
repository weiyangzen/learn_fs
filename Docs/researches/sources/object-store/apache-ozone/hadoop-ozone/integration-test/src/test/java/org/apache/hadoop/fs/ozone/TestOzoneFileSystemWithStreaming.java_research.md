# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemWithStreaming.java

Purpose: tests filesystem write behavior when Ozone datastream is enabled and automatic stream selection is controlled by a size threshold.

Important APIs/types/functions: setup enables container RATIS datastream, filesystem datastream, `ozone.fs.datastream.auto.threshold` at 2 MiB, and tuned client buffers. `testO3fsCreateFile` and `testOfsCreateFile` run the same create/read verification for O3FS and OFS paths. `createFile` asserts the wrapped stream is `SelectorOutputStream` and that the chosen underlying stream is null below threshold before close, `CapableOzoneFSOutputStream` after below-threshold close, or `CapableOzoneFSDataStreamOutput` for above-threshold data. `runTestCreateFile` verifies bytes read back exactly.

Control flow: for file sizes 1, 2, and 3 MiB, create file, write all data, inspect stream selection before and after close, then read and compare the file.

State and persistence behavior: below-threshold writes stay on the normal Ozone FS output path; above-threshold writes switch to datastream. Both modes must persist identical bytes and be readable through normal filesystem reads.

Dependencies and integration points: uses `MiniOzoneCluster`, `SelectorOutputStream`, `CapableOzoneFSOutputStream`, `CapableOzoneFSDataStreamOutput`, O3FS/OFS URI schemes, and datastream configuration keys.

Risks: relies on implementation class names and threshold boundary semantics. Writing exactly threshold-sized data is classified as below threshold. Stream selection may be lazy until sufficient bytes are written.

Test signals: catches accidental fallback or wrong stream choice, datastream read/write corruption, and differences between O3FS and OFS datastream behavior.
