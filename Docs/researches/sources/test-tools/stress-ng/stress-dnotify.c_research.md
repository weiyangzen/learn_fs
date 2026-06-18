# sources/test-tools/stress-ng/stress-dnotify.c

Purpose: implements `dnotify`, a Linux legacy directory notification stressor that verifies DN_* events are delivered through `F_NOTIFY` and realtime signals.

Important APIs/types/functions: `stress_dnotify_supported()` reads `/proc/sys/fs/dir-notify-enable`. `dnotify_handler()` captures `si_fd` from `SIGRTMIN+1`. `dnotify_exercise()` opens the watched directory, sets `F_SETSIG`, enables `F_NOTIFY` with optional `DN_MULTISHOT`, runs a helper, waits up to two seconds, validates the delivered fd, disables notifications, and closes. Helpers cover attribute, access, modify, create, delete, and rename events using `mk_file()`/`rm_file()`.

Control flow: `stress_dnotify()` installs the realtime signal handler and ignores stray SIGIO, creates a temp directory, synchronizes start, then repeatedly invokes all `dnotify_stressors[]`. Any helper failure exits via tidy with `EXIT_FAILURE`; otherwise each full pass increments bogo operations.

State and persistence behavior: `static volatile int dnotify_fd` is the only event state and is reset before each helper. Temporary files are created inside the stress-ng temp directory and removed immediately after each event, with final directory removal in deinit.

Dependencies and integration points: requires `F_NOTIFY` and `sys/select.h`; otherwise registers as unimplemented. Uses stress-ng signal/temp helpers, file helpers, and classifier `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: dnotify is legacy and may be disabled or absent in kernels. Signal delivery is asynchronous, so the two-second polling window is a functional assumption. The code validates unexpected fd values but does not fail if no event arrives before timeout, which reflects stress coverage more than strict notification testing.

Test signals: run on a Linux kernel with dnotify enabled, confirm all event helpers loop without fd mismatch failures, and check skip messages when CONFIG_DNOTIFY or `/proc/sys/fs/dir-notify-enable` is unavailable.
