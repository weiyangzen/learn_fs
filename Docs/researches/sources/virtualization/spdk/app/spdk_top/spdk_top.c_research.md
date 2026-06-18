# File Research: sources/virtualization/spdk/app/spdk_top/spdk_top.c

This file implements `spdk_top`, an ncurses-based interactive monitor for a running SPDK application. It connects to the target's JSON-RPC socket, periodically fetches framework/thread/poller/reactor data, and displays sortable, filterable tabs for threads, pollers, and cores.

The data model is built around decoded RPC structures: `rpc_thread_info`, `rpc_poller_info`, `rpc_core_info`, and `rpc_scheduler`. Global arrays hold the current snapshot for up to 1024 RPC threads, 8192 pollers, and 1024 cores. The code tracks previous counter values to show interval deltas as well as total counters. Poller history is kept in a `TAILQ` keyed by poller ID and thread ID so run and busy counters can be compared across refreshes.

RPC handling is synchronous per request. `rpc_send_req()` creates a JSON-RPC request with no parameters, sends it, polls until a response is available, rejects error responses, and returns the response object. The monitor uses `thread_get_stats`, `thread_get_pollers`, `framework_get_reactors`, `framework_get_scheduler`, and `framework_wait_init`. JSON decoder tables map fields into the local structs, with custom handling for nested core lightweight-thread arrays.

The refresh flow is split across two threads. `wait_init()` initializes curses-visible state, waits for the remote app to finish framework initialization, fetches tick rate from `framework_get_reactors`, obtains initial thread/poller/core snapshots to avoid display races, and starts `data_thread_routine()`. The data thread repeatedly fetches cores, threads, pollers, and scheduler data, updating shared globals under `g_thread_lock` and sleeping according to `g_sleep_time`. The UI thread runs `show_stats()`, handles keyboard input, tab switching, sorting/filtering popups, page navigation, detail popups, and quit.

The UI has three main tabs. The threads tab displays thread name, core, active/timed/paused poller counts, idle/busy time, CPU percentage, and busy/idle status. The pollers tab displays name, type, owning thread, run count, period, and busy status/count. The cores tab displays lcore, thread count, poller count, idle/busy time, busy percentage, interrupt state, system/IRQ/CPU percentages, and frequency. Columns can be disabled through a menu, and sorting supports primary plus secondary sort columns.

Detail popups are implemented for threads, cores, pollers, scheduler state, refresh rate, sorting, filtering, and help. Thread details include pollers running on the thread. Core details include frequency, interrupt state, idle/busy time, poller count, and thread names; selecting a thread from a core popup can open the thread detail view. Poller details show type, owning thread, run count, period, and busy count/status. Scheduler details show scheduler, period, and governor.

The curses setup uses panels, menus, color pairs, nonblocking input via `timeout(1)`, hidden cursor, and resize-aware redraws. `finish()` ends curses mode, closes the JSON-RPC client, and exits; signal handlers for SIGINT, SIGPIPE, and SIGABRT call it. Memory for decoded strings and nested arrays is freed when snapshots are replaced and again on shutdown.

Notable implementation details and caveats:

- `sort_cores()` calls `subsort_cores()` with the primary column again when the first comparison ties, so the declared secondary core sort column is not used in this file as read.
- `draw_core_win_content()` unlocks `g_thread_lock()` internally, which is unusual because callers also manage lock state around popup drawing. This coupling should be considered before refactoring popup code.
- The monitor assumes some values, such as scheduler/governor names, are stable enough not to require dynamic popup resizing.
- Error display from the data thread uses bottom-message printing while curses drawing is active, so UI synchronization depends on the existing coarse mutex and screen refresh cadence.
