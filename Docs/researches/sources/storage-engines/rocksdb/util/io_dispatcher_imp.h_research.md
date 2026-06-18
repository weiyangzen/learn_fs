# sources/storage-engines/rocksdb/util/io_dispatcher_imp.h

Purpose: declares the concrete `IODispatcherImpl` class that implements the public `IODispatcher` interface by delegating implementation details to an internal shared `Impl`.

Important APIs/types/functions: `IODispatcherImpl` has a default constructor, an options constructor taking `IODispatcherOptions`, a virtual destructor, and `SubmitJob(const std::shared_ptr<IOJob>&, std::shared_ptr<ReadSet>*)`. The private `struct Impl` is hidden behind `std::shared_ptr<Impl> impl_`.

Control flow: callers construct the dispatcher directly or through `NewIODispatcher` factories in the `.cc` file, then submit an `IOJob`. All real work is delegated to `impl_->SubmitJob`, keeping the header stable and small while allowing the implementation to use private helper types.

State and persistence behavior: the header exposes only the shared implementation pointer. It persists no on-disk state. Shared ownership lets `ReadSet` callbacks safely hold weak/shared references to dispatcher memory accounting state after public dispatcher objects move through normal lifetimes.

Dependencies/integration points: depends on `rocksdb/io_dispatcher.h` for the public interface, `IOJob`, `ReadSet`, `IODispatcherOptions`, and `Status`. It is the bridge between public RocksDB I/O dispatcher APIs and the block-based table implementation in `io_dispatcher_imp.cc`.

Risks: the PIMPL design hides invariants from the header, so API users must rely on the public `IODispatcher` contract. Lifetime is intentionally shared; changing `impl_` ownership could break `ReadSet` memory-release callbacks.

Test signals: all behavior is exercised through `io_dispatcher_test.cc` and through block-based iterator paths that call `NewIODispatcher`/`SubmitJob`.
