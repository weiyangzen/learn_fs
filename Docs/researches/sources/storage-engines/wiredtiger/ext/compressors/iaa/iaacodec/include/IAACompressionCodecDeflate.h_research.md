
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/include/IAACompressionCodecDeflate.h

Purpose: declares the C++ IAA/QPL deflate codec used behind the C extension. The namespace `DB::IAA` contains hardware job pooling, software fallback, hardware codec, and aggregate codec classes.

Important APIs/types/functions: `DeflateJobHWPool` is a singleton with `jobPoolSize = 256`, static `qpl_job *jobPool[]`, static atomic locks, `acquireJob`, `releaseJob`, and `jobPoolReady`. `SoftwareCodecDeflate` owns one software `qpl_job` through `jobSWbuffer`. `HardwareCodecDeflate` exposes `hwEnabled`, page-touching `memPageSet`, and hardware compress/decompress calls. `CompressionCodecDeflate` owns both codecs and exposes `doCompressData`, `doDecompressData`, and `getMaxCompressedDataSize`.

Control flow and state: job-pool state is process-global for the hardware path; software job state is per `SoftwareCodecDeflate` object. The aggregate class tries hardware first when enabled and falls back to software on a zero result. Dependencies are QPL, C++ atomics, WiredTiger callback types, and x86 headers. Risks include busy-waiting during pool destruction, failure paths that can leave partially initialized pool entries, range assumptions in `job_id` conversion, and hardware fallback conflating legitimate zero-byte output with failure. Test signals include concurrent job acquisition/release, pool exhaustion, constructor failure fallback, and QPL status failure injection.
