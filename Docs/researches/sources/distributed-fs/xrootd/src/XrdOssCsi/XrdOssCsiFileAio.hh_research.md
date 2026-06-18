# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiFileAio.hh

Purpose: defines the internal async state machine for checksum-aware AIO operations. It wraps the caller's `XrdSfsAio`, schedules pre/post jobs, and recycles wrapper objects.

Important APIs/types: `XrdOssCsiFileAioJob` has four job states: read step 1 locks range and submits successor AIO; read step 2 finishes short pg reads and verifies/fetches checksums; write step 1 locks range, updates/stores checksums, and submits successor AIO; write step 2 completes short writes and handles failures. `XrdOssCsiFileAio` overrides `doneRead/doneWrite` to schedule step 2, copies AIO fields in `Init()`, carries a range guard and pg options, and `Recycle()` releases locks, returns to store freelist or deletes itself, then decrements parent AIO count.

State/control: each operation uses one wrapper and embedded job object. Range locks span the successor async call and post-processing. The parent AIO receives final `Result` and callback only after checksum processing.

Risks/test signals: the header contains substantial implementation, so compile dependencies are broad. Callback buffers must remain valid across both steps; short writes are completed synchronously after async completion; failures must release locks and resync sizes. Tests should inject short read/write completions, checksum mismatch, successor AIO immediate failure, pgRead short completion, and close waiting on active jobs.
