# Research: sources/user-network-fs/samba/source4/smb_server/blob.c

Purpose: SMB server helper code for encoding and decoding passthrough SMB/SMB2 information levels into `DATA_BLOB` buffers, especially TRANS2/query/set/file-search reply formats.

Important APIs: `smbsrv_blob_grow_data()` reallocates a blob and sets length. `smbsrv_blob_fill_data()` grows and zero-fills new bytes. `smbsrv_blob_pull_string()` range-checks and delegates to `req_pull_string`. `smbsrv_blob_append_string()` reserves room, writes string data through the private `smbsrv_blob_push_string()`, stores length fields, and shrinks to actual size. `smbsrv_push_passthru_fsinfo()`, `smbsrv_push_passthru_fileinfo()`, `smbsrv_pull_passthru_sfileinfo()`, and `smbsrv_push_passthru_search()` translate raw union fields to and from wire layouts.

Control flow and state: all functions are stateless except for mutating caller-owned talloc-backed blobs and output unions. Switch statements map protocol information levels to fixed offsets, endian macros, time conversion helpers, GUID NDR blobs, EA list helpers, and chained search entry alignment.

Dependencies and integration: used by SMB server request handlers to pass NTVFS backend data through to SMB1/SMB2 wire formats. It depends on `libcli/raw`, string conversion flags, `DATA_BLOB`, talloc, and low-level put/get macros.

Risks and test signals: offset, alignment, and length-field mistakes cause client-visible protocol incompatibility. `NT_STATUS_FOOBAR` on string push/pull failure is vague. The explicit panic for zero SMB2 EAs catches backend contract violations. Signals come from raw SMB, SMB2, search, EA, stream, and file-info torture suites.
