# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssReadVFile.cc

Purpose: implements a readv decorator that can transform many small vectored reads into larger backing reads, then copy useful subranges back to the caller's `XrdOucIOVec` buffers.

Important APIs: the constructor selects `XrdCephReadVNoOp` for `passthrough`, `XrdCephReadVBasic` for `basic`, and falls back to passthrough for invalid names. `Open()` delegates to the wrapped file and mirrors its fd. `Close()` logs aggregate read timing. `ReadV()` builds an `ExtentHolder` from the caller's vectors, converts it with `m_readVAdapter`, reserves a buffer sized to the largest mapped extent, reads each mapped extent through the wrapped file's `Read()`, and copies each inner extent to the corresponding original `readV[counter].data`.

Control flow: the method verifies full reads by comparing returned bytes with mapped extent length; short positive reads return `-ESPIPE`, negative reads propagate. Other file APIs delegate unchanged to the inner object.

State and persistence: owns the wrapped file pointer and deletes it in the destructor. It keeps adapter name, adapter instance, verbose logging flag, and atomic timing counters. No data persists beyond the read buffer.

Dependencies and integration: depends on `BufferUtils`, `IXrdCephReadVAdapter`, `XrdCephReadVBasic`, `XrdCephReadVNoOp`, and the base file API.

Risks and test signals: the implementation uses `buffer.reserve(buffersize)` but not `resize()`, so `buffer.data()` points to storage with size zero; this is a serious correctness risk for backing reads and copy-out. Tests should cover passthrough and coalesced extents, copy-back ordering, short reads, and empty readv input.
