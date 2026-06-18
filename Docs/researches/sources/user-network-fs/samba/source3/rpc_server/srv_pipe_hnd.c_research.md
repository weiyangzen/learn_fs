# sources/user-network-fs/samba/source3/rpc_server/srv_pipe_hnd.c

Purpose: Implements fake-file named-pipe proxy handles for source3 RPC over `ncacn_np`. It connects SMB named-pipe opens to the local RPC server stream and provides asynchronous read/write operations.

Important APIs: `fsp_is_np()` identifies `FAKE_FILE_TYPE_NAMED_PIPE_PROXY`; `np_open()` allocates `fake_file_handle`, initializes `npa_state`, and calls `local_np_connect()` with remote/local socket addresses and session info; `np_read_in_progress()` checks the read queue length; `np_write_send()/np_write_recv()` write data through `tstream_writev_queue_send`; `np_read_send()/np_read_recv()` read PDUs through `tstream_readv_pdu_queue_send`.

Control flow and state: State is stored in `fake_file_handle->private_data` as `npa_state`, including stream, read queue, and write queue. Writes are queued and complete via `np_write_done()`. Reads use `np_ipc_readv_next_vector()` to cap reads at `UINT16_MAX`, return short reads when no more pending bytes are available, and set `is_data_outstanding` when stream pending bytes exceed the caller buffer. Zero-length reads intentionally remain pending and are completed as `NT_STATUS_PIPE_BROKEN` if the zero-read state is destroyed.

Dependencies and integration: Depends on fake file support, RPC DCE, local named-pipe client, `tevent`, `tstream`, tsocket, and NDR table declarations. This is the bridge between SMB file operations on named pipes and the in-process Samba RPC endpoint machinery.

Risks and test signals: Queue/destructor behavior is subtle; regressions can hang zero-byte reads, misreport outstanding data, or return invalid handles. Test named-pipe open/read/write, concurrent queued reads/writes, short-read behavior, client disconnects, invalid fake-file types, and zero-length read cancellation.
