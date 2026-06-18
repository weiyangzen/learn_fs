
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/src/IAACompressionCodecDeflate.cpp

Purpose: implements IAA/QPL deflate compression and decompression. It initializes a hardware QPL job pool, falls back to QPL software jobs, and uses gzip-mode dynamic-Huffman deflate streams.

Important functions: `DeflateJobHWPool::instance` provides a static singleton. The constructor logs QPL version and attempts `initJobPool`; the destructor calls `destroyJobPool`. `HardwareCodecDeflate::doCompressData` and `doDecompressData` acquire a job, populate `qpl_job`, touch output pages, execute, and release. `SoftwareCodecDeflate::getJobCodecPtr` lazily initializes a software job. `CompressionCodecDeflate` chooses hardware then software and computes a zlib-compatible deflate bound.

Control flow and state: hardware jobs are shared across threads using atomic locks; software jobs are owned by each codec instance. `iaa_message` logs through WiredTiger when compressor/session are available and also prints to stdout. Persistent output is QPL gzip-mode compressed data. Risks: QPL init errors in the software path are mostly ignored before job use; hardware pool init can leak earlier jobs on mid-loop failure; `destroyJobPool` spin-waits; stdout logging from an extension can surprise embedding applications; status errors collapse into zero length. Tests should cover hardware success, software fallback, QPL error returns, pool contention, corrupt compressed streams, and exact compressed-bound sizing.
