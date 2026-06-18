# sources/object-store/minio/cmd/mrf.go

This file implements MinIO's background MRF queue for partial operations that reached quorum but could not update every disk. It queues affected buckets or objects, persists queued work during shutdown, reloads it on startup, and drives healing once disks reconnect.

Core types are `PartialOperation` and `mrfState`. `PartialOperation` records bucket, object, version IDs or packed version bytes, erasure set and pool indexes, queue time, and whether deep bitrot healing is needed. `mrfState` owns a large buffered channel, close flags, and a wait group. `addPartialOp` drops work silently if the state is closing, closed, nil, or the channel is full. `shutdown` stops acceptance, closes the queue, streams a four-byte format/version header followed by msgp-encoded operations to `.minio.sys/buckets/.heal/mrf/list.bin` on the first writable local drive. `startMRFPersistence` scans local drives for that file, validates header format/version, decodes operations back to `opCh`, and deletes the file after successful load.

`healRoutine` consumes queued operations until global shutdown or channel close. It skips transient MinIO internal paths, waits at least one second for recent network failures, applies a dynamic sleeper, chooses normal or deep scan, and calls `healBucket` or `healObject`.

Risks: enqueue overflow drops work; shutdown persistence succeeds on only one local drive and stops on first success. Invalid/corrupt MRF files are skipped by trying another drive. Version byte decoding assumes 16-byte UUID chunks. Test signal is in generated msgp tests, not the queue/heal logic itself.
