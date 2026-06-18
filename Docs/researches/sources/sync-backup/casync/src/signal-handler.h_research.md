# sources/sync-backup/casync/src/signal-handler.h

Purpose: declares helper functions for casync signal behavior.

Important APIs/types/functions: exports `block_exit_handler`, `exit_signal_handler`, `install_exit_handler`, `sync_poll_sigset`, and `disable_sigpipe`.

Control flow/state: API manipulates process signal handlers/masks and delegates polling to a `CaSync` instance.

Dependencies/integration: includes `<signal.h>` and `casync.h`, tying this header to the main transfer object rather than keeping it fully generic.

Risks/test signals: callers must restore old masks when appropriate and avoid conflicting handlers. The interface is narrow enough that regressions should show up as hung or uninterruptible command-line tests.

Source research group: `subset-b-009122`.
