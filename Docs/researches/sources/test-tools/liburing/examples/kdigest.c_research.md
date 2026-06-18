# sources/test-tools/liburing/examples/kdigest.c

## sources/test-tools/liburing/examples/kdigest.c

Purpose: Proof-of-concept file digest pipeline using Linux AF_ALG hash sockets and io_uring reads/sends, optionally with send bundle support.

Important APIs/types/functions: `enum req_state`, `struct req`, `struct kdigest`; `reap_completions`, `submit_sends_br`, `submit_sends_linked`, `digest_file`, `get_result`; AF_ALG `socket`, `bind`, `accept`; `io_uring_prep_read`, `io_uring_prep_send`, `io_uring_prep_send_bundle`, `io_uring_prep_recv`.

Control flow: main validates algorithm/input, opens file, creates and binds AF_ALG hash socket, accepts operation socket, allocates aligned buffers, initializes ring with preferred taskrun flags and fallback, conditionally sets up buffer ring if `IORING_FEAT_RECVSEND_BUNDLE` is present, copies file data through hash socket in ordered chunks, then receives and prints digest bytes.

State and persistence: reads input file, writes into kernel crypto operation socket, stores request state and buffers in memory, no files written.

Dependencies/integration: Linux crypto user API hash support, selected algorithm in `/proc/crypto`, liburing send bundle feature for optimized path, block-device size ioctl for block inputs.

Risks: comments acknowledge incomplete error handling. Ordering relies on either buffer-ring bundle serialization or linked sends. Many early returns skip fd/ring cleanup. Bundle support is feature-gated but still experimental.

Test signals: printed digest output; errors for missing AF_ALG or algorithm; compare digest to userspace hash tools.
