# sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/sahpool-pausing.js

## Purpose
`tests/opfs/sahpool/sahpool-pausing.js` is the UI coordinator for demonstrating SAHPool VFS pause/unpause behavior across two workers. It sequences operations so one worker creates and pauses the VFS, then another worker acquires it and reads/removes it.

## Important APIs, Types, And Functions
The file defines UI logging (`mapToString`, `normalizeArgs`, `logClass`, `log`, `warn`, `error`), `toss()`, `endOfWork()`, a callback queue, `nextHandler()`, `postThen()`, `runPyramidOfDoom(W1,W2)`, and `runTests()`. `runPyramidOfDoom()` is the core sequence: W1 `vfs-acquire`, W1 `db-init`, W1 `db-query`, W1 `vfs-pause`, W2 `vfs-acquire`, W2 `db-query`, W2 `vfs-remove`.

## Control Flow
`runTests()` starts two `sahpool-worker.js` workers with distinct worker ids. It waits for both to report `initialized`, then runs the callback queue sequence. Incoming worker messages map to queue advancement, log rendering, final pass marking, or failure marking. The UI title and `#color-target` are updated on success/failure.

## State And Persistence Behavior
The coordinator stores only DOM log state, callback queue state, and worker handles. The database and VFS state live in the workers. The sequence depends on `pauseVfs()` unregistering the VFS from one worker while leaving pool contents available for another acquire/unpause path.

## Dependencies And Integration Points
It depends on a browser DOM with log controls and `sahpool-worker.js` in the same directory. It integrates with the worker protocol: `initialized`, `vfs-acquired`, `vfs-paused`, `vfs-unpaused`, `vfs-removed`, `db-inited`, `query-result`, `log`, and `error`.

## Risks And Test Signals
Risks include callback-queue deadlock if any worker message is missed, pass/fail being driven by message order rather than promises, OPFS SAH unavailability, and residual VFS state from prior failed runs. Passing signals are both workers initialized, W1 query returning rows, W1 paused, W2 acquired and queried the same data, VFS removed, and title/header marked PASS.
