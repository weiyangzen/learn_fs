## sources/user-network-fs/go-fuse/fuse/nodefs/handle.go

Purpose: portable handle map for converting Go objects to stable uint64 FUSE handles with lookup counts and generations.

Important APIs/types/functions: `handleMap` interface, `handled` embedded metadata, `_ALREADY_MSG`, `portableHandleMap`, `newPortableHandleMap`, `Register`, `Handle`, `Count`, `Decode`, `Forget`, and `Has`.

Control flow: registering assigns a new handle/generation, stores object, and initializes lookup count. Additional lookups increment counts. `Forget` decrements and removes the object when count reaches zero, clearing object handle metadata.

State and persistence: process-local maps from handles to objects and object metadata. No durable state.

Dependencies and integration: used for inode and file handle maps in nodefs connector.

Risks and test signals: generation reuse, double registration, and lookup count underflow are critical. `handle_test.go` directly covers these cases.
