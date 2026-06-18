# sources/user-network-fs/mergerfs/vendored/boost/core/detail/sp_thread_sleep.hpp

Purpose: Provides `sp_thread_sleep`, a short backoff sleep primitive for spin/yield loops.

Important APIs, types, and functions: `boost::core::sp_thread_sleep()` and compatibility `boost::detail::sp_thread_sleep` alias on Windows.

Control flow: Windows calls `Sleep(1)`. POSIX with `nanosleep` sleeps for a small timespec and may optionally block/unblock SIGCHLD around the call for pthread platforms. Fallback delegates to `sp_thread_yield`.

State and persistence behavior: No persistent state; POSIX branch temporarily manipulates thread signal masks.

Dependencies and integration points: Depends on Boost config, Windows sleep shim, `<time.h>`, optional pthread/signal headers, or yield fallback. Included by `yield_primitives.hpp`.

Risks: Signal-mask handling must restore prior state. Sleep duration and platform availability affect contention backoff behavior. Android/OHOS paths avoid pthread signal logic.

Test signals: Compile Windows, nanosleep, and fallback branches; runtime smoke test that call returns; signal-mask preservation test on pthread targets.
