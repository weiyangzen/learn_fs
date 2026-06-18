# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephBufferAlg.hh

Purpose: declares the high-level buffering algorithm interface used by XrdCeph buffered file code.

Important APIs/types/functions: pure virtual `read_aio`, `write_aio`, synchronous `read`, `write`, and `flushWriteCache`.

Control flow: callers can route synchronous or XrdSfsAio operations through one abstraction. Implementations decide when to cache, bypass, flush, or translate AIO to sync behavior.

State and persistence: no interface state. Persistent effects come from implementation write/flush behavior.

Dependencies and integration points: includes `IXrdCephBufferData`, `ICephIOAdapter`, and forward-declares `XrdSfsAio`. Implemented by `XrdCephBufferAlgSimple`.

Risks: `read` takes `volatile void *`, which forces casts in implementation and may obscure const/threading intent. `flushWriteCache` must be called by owners before close/destruction to avoid data loss; the interface cannot enforce it.

Test signals: mock algorithms for file layer tests, AIO callback completion, flush-on-close behavior, and error propagation from implementation.
