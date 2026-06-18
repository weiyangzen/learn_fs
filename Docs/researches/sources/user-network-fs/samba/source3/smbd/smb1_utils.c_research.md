# sources/user-network-fs/samba/source3/smbd/smb1_utils.c

## Purpose

`smb1_utils.c` contains helper routines used by SMB1 server code, especially compatibility helpers that are shared outside one command implementation. The file supports legacy FCB/DOS sharing behavior, RFC1002 keepalive sending, string growth in SMB buffers, SMB1 search path conversion where the terminal component can be a wildcard, and 16-bit SMB1 FID lookup.

## Important APIs, Types, and Functions

- `fcb_or_dos_open(...)`: on sharing violation, searches existing opens for the same file, vuid, pid, name, stream, and DOS/FCB deny flags, then creates a new `files_struct` sharing the existing file handle.
- `send_keepalive(int client)`: writes a four-byte NBSS keepalive packet to a client socket.
- `message_push_string(uint8_t **outbuf, const char *str, int flags)`: grows an SMB output buffer, appends a server-string encoded string using `srvstr_push`, clears unused overallocated bytes, and updates BCC.
- `filename_convert_smb1_search_path(...)`: separates the wildcard terminal component from an SMB1 search path, converts the parent directory with `filename_convert_dirfsp`, and returns the directory FSP, converted parent name, and mask.
- `file_fsp(struct smb_request *req, uint16_t fid)`: resolves a 16-bit SMB1 FID to a non-closing `files_struct`, honoring chained requests via `req->chain_fsp`.

## Control Flow

`fcb_or_dos_open` first rejects calls without DOS/FCB private flags. It computes the file id from the stat buffer, iterates matching file-id opens on the server connection, and checks request identity, deny flags, write access, base name, and stream name. When a match is found, executable names are refused for `DENY_DOS`, then `file_new` creates a second FSP whose `fh` pointer and selected metadata are copied from the original. The file-handle refcount is incremented and permissions are recalculated from the requested access mask.

`message_push_string` calculates an intentionally generous growth amount for encoded output, reallocates the buffer with talloc, pushes the string at the old buffer end, validates wrap/size assumptions, zeroes unused growth, updates SMB BCC, and returns the encoded byte count.

`filename_convert_smb1_search_path` extracts an optional snapshot token, obtains the original last component as the wildcard mask, maps empty masks to `"*"`, removes the terminal component from the input string in-place, and converts the remaining parent path. Ownership of the returned `smb_filename` and mask is moved to the caller's context.

`file_fsp` first returns a valid chained FSP if present. Otherwise it looks up the SMB1 open record with `smb1srv_open_lookup`, rejects missing or closing FSPs, caches the result on `req->chain_fsp`, invalidates cached DOS attributes, and returns the FSP.

## State and Persistence Behavior

`fcb_or_dos_open` creates a new open record that shares an existing underlying file handle and increments the handle refcount, so close semantics depend on balanced `file_free`/close behavior later. `file_fsp` mutates `req->chain_fsp` as a per-request cache and invalidates cached DOS attributes on the FSP name. `filename_convert_smb1_search_path` mutates `name_in` by truncating the terminal path component. `message_push_string` reallocates and replaces the caller's output-buffer pointer.

## Dependencies and Integration Points

The file integrates with file-id lookup, Samba file handle refcounting, `smbXsrv_open` SMB1 open lookup, VFS file-id generation, SMB string conversion, path conversion, snapshot-token extraction, and low-level write helpers. `smb1_trans2.c` uses `fcb_or_dos_open`, `filename_convert_smb1_search_path`, and `file_fsp`.

## Risks and Edge Cases

`fcb_or_dos_open` deliberately implements legacy semantics by aliasing an existing file handle; bugs here can produce incorrect access rights, leaked references, or surprising sharing behavior. The helper assumes names and streams compare as expected and refuses executable DOS-deny reuse. `message_push_string` must preserve buffer ownership and BCC correctness after realloc; failure after realloc returns `-1` without assigning `*outbuf` to the temporary buffer, which callers must handle. `filename_convert_smb1_search_path` edits its input path in place, so callers must pass mutable storage and not expect the original full path afterwards. `file_fsp` caches a pointer in the request; callers must not use it after the FSP begins closing.

## Test Signals

Signals include SMB1 open tests for DOS/FCB deny fallback, chained SMB1 commands that reuse `chain_fsp`, wildcard search tests for root and nested directories, snapshot path searches, Unicode and ASCII string append tests for BCC/length consistency, and keepalive write error handling on disconnected sockets.
