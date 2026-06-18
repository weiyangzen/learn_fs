# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcMultistream.cc

Purpose: Implements multi-stream pull transfers for HTTP TPC using libcurl multi handles, duplicated `State` objects, and reordering buffers in `Stream`.

Important APIs/types/functions: Internal `MultiCurlHandler` manages active/available curl handles, transfer scheduling, completion accounting, buffer-aware throttling, and error aggregation. `TPCHandler::RunCurlWithStreamsImpl` performs the multi-stream transfer loop. `RunCurlWithStreams` wraps implementation errors and deletes allocated `State` objects.

Control flow: The first state is moved from the caller and duplicated up to `streams * m_pipelining_multiplier`. A libcurl multi handle is configured with host connection limits, a chunked 202 response is started, byte ranges are scheduled in `m_block_size` chunks, and the loop alternates `curl_multi_perform`, PMark start, completion harvesting, new range scheduling, progress markers, timeout checks, and `curl_multi_wait`. Finalization flushes stream buffers, validates full content offset, closes the file, sends success/failure chunk, and terminates chunked response.

State and persistence: Runtime state includes current offset, active/idle handles, aggregate bytes/status/error, and reordering buffers in the shared `Stream`. The only durable effect is local file writes through the SFS file handle.

Dependencies and integration points: Uses `TPC::State`, `TPC::Stream`, libcurl multi API, TPC perf marker methods, PMark manager, and XRootD logging/error response functions.

Risks: Manual `new`/`delete` for `State` objects requires all exception paths to clean up. Buffer availability controls concurrency; logic bugs can deadlock or exhaust memory. Progress timeout currently compares `current_offset`, which reflects scheduled bytes, not necessarily flushed bytes. Multi-stream is pull-only in this code path.

Test signals: Multi-stream pulls with 1, 2, and high stream counts, remote failures on one range, buffer exhaustion, timeout with stalled server, final short block, interrupted chunk response, and verification that the final file is complete and ordered.
