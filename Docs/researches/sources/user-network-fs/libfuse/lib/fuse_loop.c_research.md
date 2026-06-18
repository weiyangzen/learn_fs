# sources/user-network-fs/libfuse/lib/fuse_loop.c

## Purpose

`fuse_loop.c` implements the single-threaded low-level session loop, `fuse_session_loop`. It repeatedly receives one request buffer from a `struct fuse_session`, processes it synchronously, and exits when the session is marked exited, receive returns EOF/error, or a session error is recorded.

## Important APIs, Types, And Functions

The only function defined is `int fuse_session_loop(struct fuse_session *se)`. It uses `struct fuse_buf`, `fuse_session_exited`, `fuse_session_receive_buf_internal`, `fuse_session_process_buf`, `fuse_buf_free`, and, when configured, `fuse_uring_stop`.

## Control Flow

The function initializes a reusable `struct fuse_buf` with `mem = NULL`, then loops while `!fuse_session_exited(se)`. Each iteration calls `fuse_session_receive_buf_internal(se, &fbuf, NULL)`. `-EINTR` is ignored and retried. Nonpositive results break the loop. Positive results are processed by `fuse_session_process_buf(se, &fbuf)`.

After the loop, the receive buffer is freed. A positive last receive length is normalized to success (`0`). If `se->error` is nonzero, that value overrides the result. If the session has an io_uring pool, `fuse_uring_stop(se)` is called before returning.

## State And Persistence Behavior

The loop maintains only the reusable request buffer and return code locally. It mutates session state indirectly through receive and process calls; those paths can allocate requests, update request lists, dispatch operations, set `se->error`, or mark the session exited. There is no persistence beyond process memory and the mounted FUSE device interaction.

## Dependencies And Integration Points

The file includes `fuse_config.h`, `fuse_lowlevel.h`, `fuse_i.h`, and `fuse_uring_i.h`. It is the low-level loop used directly by low-level filesystems and indirectly by high-level `fuse_loop` when remembered-node cleanup is not needed.

It expects the session to have been created and mounted already, and it reads from the session's main fd through `fuse_session_receive_buf_internal`. For high-level filesystems, request processing eventually dispatches into `fuse_path_ops` from `fuse.c`.

## Risks And Edge Cases

The loop is strictly single-threaded, so a blocking callback prevents all other requests from being processed. It treats `-EINTR` during receive as harmless, but any other negative receive result exits. Since it calls `fuse_session_process_buf` rather than the internal channel-aware variant, there is no cloned channel passed to processing.

The function stops io_uring only after the main loop exits. If processing code sets `se->error`, that session error overrides a normal receive exit, which is useful but can obscure the original receive result.

## Test Signals

Tests should use a fake or instrumented session receive path to cover EINTR retry, positive receive and process dispatch, zero/negative termination, positive-length normalization to zero, `se->error` override, and io_uring stop on exit. Integration tests should compare behavior with `fuse_session_loop_mt_312` under the same mounted low-level filesystem.
