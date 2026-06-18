# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseThread.cpp

Purpose: implements a small thread wrapper that runs a `fspp::fuse::Fuse` instance in foreground mode during tests.

Important APIs/functions: constructor stores a raw `Fuse*`; `start(mountDir, fuseOptions)` launches a `boost::thread` that calls `runInForeground()`; `stop()` calls `Fuse::stop()` and waits for clean shutdown.

Control flow: `start()` spawns the child thread, busy-waits until `Fuse::running()` reports true, and on Apple sleeps briefly because macFUSE reports readiness early. `stop()` requests shutdown, joins with a 10 second timeout, asserts success, then busy-waits until `running()` is false.

State/persistence: holds only a non-owning pointer and the boost thread. No persistent state.

Dependencies/integration: depends on Boost thread/chrono, Boost filesystem path, cpp-utils assert, and `fspp::fuse::Fuse`.

Risks: busy-wait loops can spin CPU if FUSE never changes state. The raw pointer requires the caller to outlive the thread wrapper. The hard 10 second assertion makes hangs fail fast in tests.

Test signals: exercised indirectly by `FuseTest::TempTestFS` lifecycle.
