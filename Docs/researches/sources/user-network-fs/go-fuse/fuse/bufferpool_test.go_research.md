## sources/user-network-fs/go-fuse/fuse/bufferpool_test.go

Purpose: verifies buffer pool allocation/free accounting and integration with server request processing.

Important APIs/types/functions: `TestBufferPool` exercises `AllocBuffer`, `FreeBuffer`, and `counters`. `readFS` implements a tiny raw FS with `Open`, `Read`, and `Lookup`. `TestBufferPoolRequestHandler` mounts it and performs reads.

Control flow: direct unit test checks page rounding and counter balance. Integration test routes kernel reads through raw callbacks and expects buffers to be returned after request completion.

State and persistence: temporary mount plus buffer pool counters. `readFS` serves static data.

Dependencies and integration: targets `fuse.Server`, `RawFileSystem`, request allocation, and read result lifecycle.

Risks and test signals: catches leaks where buffers remain checked out after requests, and regressions where read result `Done`/response paths skip frees.
