# sources/distributed-fs/tahoe-lafs/src/allmydata/nodemaker.py

## Purpose
Provides `NodeMaker`, the factory that turns Tahoe capability strings into in-memory file/directory node objects and creates new mutable or immutable nodes. It is the bridge between URI parsing and higher-level filesystem objects.

## APIs, Types, And Control Flow
`NodeMaker` implements `INodeMaker`. `create_from_cap(writecap, readcap, deep_immutable, name)` chooses a usable cap, parses it with `uri.from_string`, dispatches by URI type in `_create_from_single_cap`, wraps unknown caps in `UnknownNode`, and wraps blacklisted storage indexes in `ProhibitedNode`. It can create literal, immutable CHK, immutable verifier, mutable SSK/MDMF, and directory nodes. `create_mutable_file` generates or accepts RSA key pairs, initializes a `MutableFileNode`, and returns a Deferred. `create_new_mutable_directory` validates children and packs them into `MutableData`; `create_immutable_directory` packs deep-immutable children, uploads CHK data, then creates a directory wrapper.

## State, Persistence, And Integration
Holds references to the storage broker, secret holder, history, uploader, terminator, encoding parameters, mutable default format, key generator, and optional blacklist. It caches node objects in a `WeakValueDictionary` keyed by cap and mutability/deep-immutable mode; despite a stale comment, the implementation caches mutable nodes and avoids caching unknown/prohibited wrappers. Persistent state is produced indirectly through uploads, mutable publishes, and storage interactions performed by the created nodes.

## Risks And Test Signals
Risks center on URI-type coverage, cache correctness, mutable identity behavior, and blacklist checks for nodes whose storage index is absent or expensive. Directory creation depends on `pack_children` metadata shape and writekey handling. Test signals are `test_filenode.py`, mutable/immutable upload/download tests, no-network tests, blacklist tests, and directory tests that validate cap parsing and factory behavior.
