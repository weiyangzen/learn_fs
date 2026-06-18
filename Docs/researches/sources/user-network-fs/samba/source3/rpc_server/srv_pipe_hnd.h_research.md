# sources/user-network-fs/samba/source3/rpc_server/srv_pipe_hnd.h

Purpose: Declares the named-pipe fake-file proxy API used by SMB file handling and RPC server code.

Important APIs: Exposes `fsp_is_np()`, `np_open()`, `np_read_in_progress()`, asynchronous `np_write_send()/recv()`, and asynchronous `np_read_send()/recv()`. Forward declarations include `tsocket_address` and `pipes_struct`; signatures use `fake_file_handle`, `auth_session_info`, `tevent_context`, `messaging_context`, and `dcesrv_context`.

Control flow and state: The header defines no storage; callers receive a `fake_file_handle` that owns implementation state created in `np_open()`. Read/write completion follows Samba `tevent_req` conventions.

Dependencies and integration: Integrated with source3 fake-file and local RPC named-pipe code. Callers must honor async send/recv pairing and handle `NTSTATUS` completion.

Risks and test signals: API misuse can leak handles or leave requests pending. Compile coverage and named-pipe RPC integration tests are the main signals.
