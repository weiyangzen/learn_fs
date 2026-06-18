# sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessBaseStore.h

Purpose: abstract base-store interface used by `ParallelAccessStore` to load and remove keyed resources from the underlying persistent store.

Important APIs/types/functions: template `ParallelAccessBaseStore<Resource, Key>`, virtual destructor, `loadFromBaseStore`, `removeFromBaseStore(unique_ref<Resource>)`, and `removeFromBaseStore(const blockstore::BlockId&)`.

Control flow: pure virtual interface only; implementers supply load/remove semantics.

State and persistence behavior: abstracts persistent resource access. Loading returns optional ownership of a resource; removal can be by loaded resource or by key.

Dependencies and integration points: uses `cpputils::unique_ref`, `boost::optional`, and `blockstore::BlockId`. The template key type is generic, but one remove overload is fixed to `BlockId`, coupling the interface to blockstore IDs.

Risks and test signals: mixed generic `Key` and concrete `BlockId` in removal is an API smell and may constrain reuse. Implementations must honor ownership and deletion guarantees expected by `ParallelAccessStore`.
