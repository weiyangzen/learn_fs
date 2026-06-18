# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2gtk.py

## Purpose

`subunit2gtk.py` displays a subunit stream in a GTK progress window. It is a graphical consumer of v2 subunit events.

## Important APIs, Types, and Functions

`GTKTestResult` is a `unittest.TestResult`-like receiver that tracks `tests`, `failures`, `errors`, `skips`, `xfails`, `uxsuccesses`, `progress`, and `last_time`. It builds GTK widgets including a window, progress bar, labels, and scrolling details text. Outcome methods update counters and append test ids. `progress()` applies subunit progress constants to a `ProgressModel`. `main()` starts a reader thread that runs `ByteStreamToStreamResult(sys.stdin).run(StreamToExtendedDecorator(result))`, enters `Gtk.main()`, and exits nonzero if failures occurred.

## Control Flow

The GTK main thread owns the UI. The worker thread parses stdin and calls result methods as events arrive. UI mutations are scheduled with `GObject.idle_add` to avoid direct GTK calls from the reader thread. `stopTestRun` schedules `Gtk.main_quit`. The progress bar displays `pos/width` when width is known, otherwise it uses pulse mode.

## State and Persistence Behavior

All state is in-memory UI/result state. No files are written. The script persists only the process exit status based on `wasSuccessful`.

## Dependencies and Integration Points

It depends on PyGObject (`gi`, `Gtk`, `GObject`), `testtools.StreamToExtendedDecorator`, `subunit.ByteStreamToStreamResult`, and `subunit.progress_model.ProgressModel`. It is optional and environment-sensitive compared with the non-GUI filters.

## Risks and Test Signals

GUI availability is the main risk: missing GI bindings or headless environments will fail at import/runtime. Threaded event handling depends on `GObject.threads_init`, which is old GTK-era API. There are no direct tests in this subset, so validation should be manual or an integration smoke test with a small v2 stream in a GTK-capable environment.
