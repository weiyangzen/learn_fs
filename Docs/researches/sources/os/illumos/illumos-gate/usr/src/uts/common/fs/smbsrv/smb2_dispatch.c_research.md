# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_dispatch.c

Read completely. This file is the SMB2/SMB3 dispatch core. It maps SMB2 command codes to handlers, accepts new requests from the session reader, decrypts SMB3 transform messages, validates and dispatches compound commands, manages credits, signing, encryption, async interim responses, error responses, FID lookup, statistics, and postwork.

`smb2_disp_table` binds commands such as negotiate, session setup, logoff, tree connect, create, close, flush, read/write, lock, ioctl, cancel, echo, query/set info, change notify, and oplock break. `smb2sr_newrq()` validates SMB2 magic, decrypts encrypted SMB3 messages with `smb3_decrypt_msg()`, scans compound headers to validate message-ID ranges and credit charges, special-cases cancel requests, and queues normal work on the server taskq.

`smb2sr_work()` is the central compound-command loop. It decodes headers, writes tentative reply headers, shadows each command payload, enforces related-operation inheritance for user/tree/file state, verifies sessions and tree connects, enforces session/tree encryption policies, checks SMB2 signatures, adjusts credits, invokes the command handler, encodes final headers, signs or encrypts replies, flushes durable handle nvlist updates, sends the reply, runs postwork, and frees the request.

Async handling is implemented by `smb2sr_go_async()`, `smb2sr_go_async_indefinite()`, and `smb2sr_send_interim()`. These send SMB2 `STATUS_PENDING` interim responses, update credits at interim time, and preserve or reset compound reply state depending on bounded vs indefinite blocking behavior.

Important exported utilities include `smb2_decode_header()`, `smb2_encode_header()`, `smb2_send_reply()`, `smb2sr_put_error*()`, `smb2sr_lookup_fid()`, dispatch stats init/fini/update, and postwork queue helpers. The file is a high-risk integration point because most SMB2 security, credit, async, encryption, and compound semantics converge here.
