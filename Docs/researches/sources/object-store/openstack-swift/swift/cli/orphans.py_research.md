# sources/object-store/openstack-swift/swift/cli/orphans.py

Purpose: lists and optionally signals Swift processes that are not represented by pid files under the Swift run directory.

Important APIs: `main()` parses age, kill signal, wide output, and alternate run directory. It reads `.pid` and `.pid.d` files, includes child processes of those PIDs, scans `ps`, filters Swift commands, excludes known live PIDs and commands containing `once`, then prints or signals the remaining old processes.

Control flow: run-dir walk builds the protected PID set. Process scanning parses elapsed time like `oldies.py`, applies regex matching for `/usr/bin/python[23]? /usr(/local)?/bin/swift-`, skips protected/once processes, and collects old orphan rows. Optional signal names or numbers are resolved and sent via `os.kill()`.

State and persistence: reads pid files and process table; optional side effect is sending signals to matched processes.

Dependencies and integration: uses `swift.common.manager.RUN_DIR`, Linux `ps`, signal constants, and Swift daemon pid-file conventions.

Risks: stale/missing pid files can cause legitimate daemons to be reported as orphaned. Signal mode is destructive. Regex does not cover all possible install paths. Tests should mock run-dir files, child PID discovery, elapsed parsing, `once` exclusion, output clipping, signal translation, and kill calls.
