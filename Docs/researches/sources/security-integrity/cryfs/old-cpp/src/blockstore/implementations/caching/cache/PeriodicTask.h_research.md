# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.h

Purpose: Declares the legacy C++ cache periodic task helper.

Important APIs and types: `PeriodicTask` stores a `std::function<void()>`, a `boost::chrono::nanoseconds` interval, and a `cpputils::LoopThread`. Copy/assign are disabled.

Control flow: Public construction starts the thread through the implementation file. `_loopIteration` is the repeating callback passed to `LoopThread`.

State and persistence behavior: In-memory only, with side effects determined by the task callback. Member order is explicitly part of lifecycle safety: `_thread` is last so it is destructed first.

Dependencies and integration points: Included by `Cache.h` for automatic cache purging.

Risks: The class has no explicit stop method, relying on `LoopThread` destruction semantics. Users must ensure the callback target outlives the running thread.

Test signals: Validated indirectly by cache construction/destruction and purge behavior.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.h` completely for this pass (32 lines, 771 bytes).
