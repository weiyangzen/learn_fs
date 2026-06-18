<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.cc

Purpose: Implements the pooled callback adapter from POSIX async completion to `XrdSfsAio` completion. It lets PSS reuse callback objects and transfer async results and page-read checksum vectors back to server request objects.

Important APIs/types/functions: Static members `myMutex`, `freeCB`, `numFree`, and `maxFree` implement the free list. `Alloc()` pops a callback from the pool or allocates one, initializes `theAIOP`, `isWrite`, and `isPGrw`. `Complete()` maps negative results to `-errno`, copies checksum vectors for successful page reads, calls `doneWrite()` or `doneRead()`, and recycles. `Recycle()` either deletes the callback if the pool is full or pushes it onto the free list after clearing `csVec`.

Control flow and state: A union stores either the active `XrdSfsAio*` or next free-list pointer. Pool mutations are mutex-protected; active completion state is per callback. `maxFree` defaults to 100 and can be set through the header.

Dependencies/integration: Used exclusively by `XrdPssAio.cc` and derives from `XrdPosixCallBackIO`. Completion assumes `errno` still represents the async failure when `result < 0`.

Risks and test signals: Reliance on global `errno` at callback time can be fragile if async providers pass negative errno codes differently. Tests should cover negative completions, checksum copyback, read vs write done callbacks, pool growth/limit behavior, and concurrent callback allocation/recycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.cc -->
