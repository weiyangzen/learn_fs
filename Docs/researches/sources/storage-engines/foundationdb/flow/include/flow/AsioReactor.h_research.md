# sources/storage-engines/foundationdb/flow/include/flow/AsioReactor.h

Purpose: declares the Boost.Asio-backed reactor used by Flow net2.

Important APIs/types/functions: namespace `N2`; classes `ASIOReactor`, Linux nested `EventFD`, abstract `Task`, `OrderedTask`, and globals/types `Net2`, `Peer`, `Connection`, `g_net2`.

Control flow: `ASIOReactor` owns an `io_service`, work guard, first timer, and wake/react/sleep APIs implemented elsewhere. Linux `EventFD` opens an `eventfd`, wraps it in an Asio stream descriptor, and returns Flow `Future<int64_t>` from async reads through a promise.

State/persistence: reactor owns Asio event-loop state. `EventFD` owns a file descriptor and read buffer until destruction.

Dependencies/integration: Boost.Asio, Linux `eventfd`, Flow futures, `g_network->global(INetwork::enEventFD)`, and net2 internals.

Risks: async read handler captures a pointer to `fdVal`; object lifetime must outlive pending reads. `sd.close()` is assumed to close the fd. EventFD is Linux-only; other platforms use different wake mechanisms.

Test signals: net2 event-loop tests, wake/read behavior on Linux, and network benchmark scheduling.
