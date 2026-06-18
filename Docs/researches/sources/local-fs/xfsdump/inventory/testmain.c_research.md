# File Research: sources/local-fs/xfsdump/inventory/testmain.c

Legacy low-level debug/test driver for the inventory subsystem.

Key functions:
- `write_test()` generates fake filesystem/session/media UUIDs, opens inventory write sessions, creates streams/mediafiles, and optionally writes packed session info for reconstruction testing.
- `query_test()` exercises index printing and last-session/last-time queries.
- `recons_test()` reads serialized session buffers and reinserts them.
- `delete_test()` tests media-object deletion from a saved `moids` file.
- `sess_queries_byuuid()` and `sess_queries_bylabel()` query and print a session.
- `main()` parses a local debug command set and delegates to the above.

Notable observations:
- The file is explicitly described as hacked-up low-level debugging code.
- Several calls no longer match current public prototypes, for example missing `fsidp` arguments to query functions and old `inv_put_sessioninfo()` shape in reconstruction code.
- Uses old UUID APIs such as `uuid_create()`/`uuid_to_string()` in places, while other files use libuuid-style APIs.
- `main()` lacks an explicit return type, reflecting old C style.
- Best treated as historical/debug scaffolding, not a maintained test suite.
