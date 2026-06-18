# sources/storage-engines/foundationdb/fdbcli/FlowLineNoise.cpp

Purpose: Provides asynchronous line input, completion, hints, history, and keyboard-interrupt handling for fdbcli using linenoise on Unix-like platforms and stdin fallback elsewhere.

Important APIs/types/functions: `LineNoiseReader` implements `IThreadPoolReceiver`; nested `Read` actions carry a prompt and `ThreadReturnPromise<Optional<std::string>>`; `LineNoise::LineNoise`, destructor, `read`, `onKeyboardInterrupt`, `historyAdd`, `historyLoad`, and `historySave`; helper `waitKeyboardInterrupt`. It uses linenoise callbacks when `HAVE_LINENOISE` is true and Boost.Asio signal handling for SIGINT.

Control flow: The constructor creates a generic thread pool, installs a `LineNoiseReader`, configures linenoise max history, multiline mode, completion callback, hints callback, and free callback. Linenoise callbacks run in the reader thread but call `onMainThread(...).getBlocking()` to safely invoke fdbcli completion/hint functions on the main Flow thread. `read` posts an action to the thread pool and returns a future. The reader turns Ctrl-C/EAGAIN into an empty string, EOF into absent optional, and exceptions into errors.

State and persistence behavior: Maintains a thread pool and linenoise global callback functions. History is persisted only when `historyLoad`/`historySave` are called with a filename; this file just delegates to linenoise.

Dependencies and integration points: Integrates Flow thread pools, `onMainThread`, network global ASIO service, linenoise, Boost.Asio, and fdbcli interactive command handling.

Risks: Linenoise callback storage uses static function objects, so multiple `LineNoise` instances would overwrite callbacks. Completion captures `line` and a local vector across synchronous `getBlocking`, which relies on callback execution remaining synchronous. Non-Unix fallback lacks completion/history behavior.

Test signals: Interactive behavior is hard to automate, but tests can cover fallback reads, future completion, Ctrl-C handling, callback invocation via `onMainThread`, history load/save error propagation, and clean thread-pool shutdown.
