# sources/sync-backup/bup/test/int/test_protocol.py

Purpose: round-trip test for protocol serialization of VFS item records.

Important APIs/types/functions: `BytesIO`, `vfs.Root`, `protocol.write_item`, and `protocol.read_item`.

Control flow: constructs a `vfs.Root(meta=13)`, writes it to an in-memory byte stream, logs the raw stream for debugging, rewinds, and asserts the deserialized item equals the original.

State and persistence behavior: no persistent state; only stream position and bytes in memory.

Dependencies/integration points: covers the transport encoding used when repository/VFS objects cross protocol boundaries. It depends on VFS namedtuple equality and the protocol's type tagging for item subclasses.

Risks and test signals: narrow coverage exercises only a `Root` item with integer metadata. The signal is exact object equality after serialization and deserialization.
