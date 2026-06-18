# sources/sync-backup/casync/src/signal-handler.c

Purpose: centralizes signal blocking, exit handler installation, polling integration, and SIGPIPE suppression for the casync tool.

Important APIs/types/functions: `block_exit_handler`, `exit_signal_handler`, `install_exit_handler`, `sync_poll_sigset`, and `disable_sigpipe`. The file uses `CaSync` polling via `ca_sync_poll`.

Control flow/state: `block_exit_handler` changes the calling thread signal mask for SIGINT/SIGTERM. `install_exit_handler` installs a supplied handler for both. `sync_poll_sigset` temporarily unblocks exit signals around `ca_sync_poll` using `ppoll`-style semantics. `disable_sigpipe` ignores SIGPIPE process-wide.

Dependencies/integration: includes `casync.h`, `signal-handler.h`, and `util.h`; used by command-line transfer loops.

Risks/test signals: signal disposition and masks are process/thread global effects, so ordering matters when embedded. Tests likely cover behavior only through interruptible tool scenarios, not unit tests.

Source research group: `subset-b-009122`.
