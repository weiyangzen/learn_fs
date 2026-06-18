# sources/user-network-fs/bazil-fuse/fuseutil/fuseutil.go

Purpose: `fuseutil.go` provides a small helper for serving read requests from an in-memory byte slice representing the entire file content.

Important APIs, types, and functions: `HandleRead(req *fuse.ReadRequest, resp *fuse.ReadResponse, data []byte)` adjusts `data` by `req.Offset` and `req.Size`, copies the selected range into `resp.Data`, and shrinks `resp.Data` to the number of copied bytes.

Control flow: If the read offset is at or beyond EOF, the helper returns an empty response. Otherwise it slices from the offset, truncates to the requested size, copies into `resp.Data[:req.Size]`, and sets `resp.Data = resp.Data[:n]`.

State and persistence behavior: Stateless. It mutates only the supplied response buffer.

Dependencies and integration points: Used by test and example handles that implement `Read`. It depends on `bazil.org/fuse` request/response types.

Risks: The caller must ensure `resp.Data` has length at least `req.Size`; otherwise `resp.Data[:req.Size]` will panic. The helper assumes `req.Offset` is non-negative as provided by kernel/FUSE semantics.

Test signals: Many `serve_test.go` read-related tests rely on this helper, including `Read`, direct read, invalidation, poll, and mmap-backed read paths.
