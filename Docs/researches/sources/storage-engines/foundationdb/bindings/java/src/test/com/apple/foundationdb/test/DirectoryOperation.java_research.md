# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryOperation.java

Purpose: enum listing every stack-machine directory operation understood by the Java directory extensions.

Important APIs and flow: constants cover directory/subspace/layer creation, current handle switching, error index selection, create/open/move/remove/list/exists, layer checks, subspace pack/unpack/range/contains/open, logging, and prefix stripping. The `createsDirectory` flag marks operations that append a directory-like handle and therefore need a null placeholder on error.

State and persistence: no runtime state beyond enum metadata. Integration is direct with `DirectoryExtension`, `AsyncDirectoryExtension`, and `DirectoryUtil.pushError`. Risks are contract drift: adding an operation in one binding or extension without updating this enum breaks `valueOf(inst.op)` dispatch. Test signal comes from cross-binding directory workloads that expect handle list alignment after both success and failure.
