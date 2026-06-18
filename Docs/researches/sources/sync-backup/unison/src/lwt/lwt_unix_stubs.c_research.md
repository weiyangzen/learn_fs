# sources/sync-backup/unison/src/lwt/lwt_unix_stubs.c

Purpose: Windows-focused OCaml C stubs for Unison’s bundled Lwt/Unix async I/O, plus buffer blits, sockets, named pipes, directory-change notifications, and path helpers.

Important APIs: buffer blits `ml_blit_*_buffer`; completion management `init_lwt`, `win_wait`, `get_queue`; fd wrapping `win_wrap_fd`, `win_wrap_overlapped`, `win_kill_threads`; async I/O `win_read`, `win_write`; socket wait helpers `win_register_wait`, `win_check_connection`, `win_socket`; named pipe helpers `win_pipe_in/out`; watcher helpers `win_readdirtorychanges`, `win_parse_directory_changes`, `win_open_directory`; path helper `win_long_path_name`.

Control flow: overlapped handles use `ReadFileEx`/`WriteFileEx` with APC completion callbacks. Synchronous handles queue work to helper threads that call blocking `ReadFile`/`WriteFile`, then queue an APC back to the main thread. Completions are stored in a dynamically resized queue and drained into an OCaml callback from `win_wait`.

State/persistence: global completion callback root, completion queue, helper thread handles, main thread handle, dummy event, and pipe serial. Kernel handles and sockets are allocated and returned to OCaml.

Dependencies/integration: Windows Winsock2/Win32 APIs, OCaml runtime compatibility macros, Bigarray buffers, and Unison's Lwt OCaml layer.

Risks: global queue is not obviously synchronized beyond intended main/APC threading. Helper thread lifecycle must be killed to avoid leaks. `win_readdirtorychanges` name contains a typo that likely matches existing OCaml external binding. Buffer offsets are unchecked in C.

Test signals: Windows tests should exercise async read/write, waits/timeouts, socket connect/accept readiness, directory-change parsing, long-path normalization, named-pipe inheritance/cloexec, and clean helper-thread shutdown.
