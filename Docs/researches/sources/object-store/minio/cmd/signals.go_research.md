# sources/object-store/minio/cmd/signals.go

Purpose: This file handles OS, HTTP-server, and service-control signals for graceful shutdown and restart. It coordinates shutting down heal state, global context, HTTP server, object layer, Console, event targets, profilers, log output, and systemd status notifications.

Important APIs and types: `shutdownHealMRFWithTimeout` bounds MRF heal shutdown to one minute. `handleSignals` runs the signal loop and defines local `exit` and `stopProcess` helpers. It consumes `globalHTTPServerErrorCh`, `globalOSSignalCh`, and `globalServiceSignalCh`, and handles `serviceRestart` and `serviceStop`.

Control flow: On HTTP server error, the handler logs it, stops the process, and exits with success/failure based on shutdown result. On OS interrupt/TERM/QUIT, it logs the signal, notifies systemd stopping, stops the process, and exits. On service restart, it notifies reloading, stops the process, calls `restartProcess`, conditionally notifies ready, logs restart errors, and exits based on combined stop/restart success. On service stop, it notifies stopping and exits after shutdown. `stopProcess` first shuts down heal MRF, cancels `GlobalContext`, shuts down HTTP server, object layer, Console, and event targets.

State and persistence behavior: The code closes global log output, stops active profilers, cancels global runtime context, shuts down runtime services, removes notification targets, and exits the process. There is no durable state except whatever subsystem shutdowns flush.

Dependencies and integration points: It integrates with `service.go`, systemd daemon notifications, HTTP server abstraction, object layer shutdown, Console server, event notifier, profiler registry, logger, and heal MRF state. `serverMain` starts this goroutine after registering OS signals.

Risks: `exit` calls `os.Exit`, so deferred cleanup in other goroutines will not run. Shutdown order is important: MRF shutdown happens before S3 operation cancellation. The one-minute MRF timeout prevents indefinite waits but can leave work unfinished. Service reload/freeze signals are enumerated elsewhere but not handled in this switch. Any nil/global function assumptions must hold during partial startup failures.

Test signals: No direct tests are present. Indirect signals are clean test-server teardown paths and operational behavior during SIGTERM, service stop, and restart.
