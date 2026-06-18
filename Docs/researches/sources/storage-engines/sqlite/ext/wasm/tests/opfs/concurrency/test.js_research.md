# sources/storage-engines/sqlite/ext/wasm/tests/opfs/concurrency/test.js

## Purpose
`tests/opfs/concurrency/test.js` is the UI coordinator for OPFS concurrency stress testing. It launches multiple workers against the same OPFS database, collects progress and pass/fail messages, and renders test output into the page.

## Important APIs, Types, And Functions
The script defines DOM logging helpers, `wait()`, URL-derived `options`, a `workers` array with `post()` and `counts`, `calcTime()`, `checkFinished()`, `workers.onmessage()`, and the launch button handler. It builds quick links for common combinations of `interval`, `iterations`, `workers`, `vfs`, `opfsVerbose`, and `unlock-asap`.

## Control Flow
On load, it prepares log rendering and option parsing from script and page URL arguments. Clicking `#gogogo` removes the button, constructs `worker.js` URL arguments, launches the requested number of workers, gives the first worker responsibility for optional DB unlinking unless `no-unlink` is set, then assigns a shared message handler. Once all workers report `loaded`, it records start time and broadcasts `run`. It records `finished` and `failed` counts and reports aggregate status when all workers are done.

## State And Persistence Behavior
The UI stores no database state itself. It persists log-order preference in `localStorage`. Test state is worker count, loaded/pass/fail counters, start time, and DOM output. The shared database state is created and mutated by workers in OPFS.

## Dependencies And Integration Points
It depends on a browser DOM containing `#gogogo`, `#test-output`, `#cb-log-reverse`, and `#testlinks`, plus `worker.js` in the same directory. It integrates with the worker message protocol: `loaded`, `stdout`, `stderr`, `error`, `finished`, and `failed`.

## Risks And Test Signals
Risks include too many workers/short intervals causing legitimate busy contention, option parsing defaults hiding invalid values, early worker messages before handler assignment, and first-worker unlink races if startup order changes. Passing signals are all workers loaded, periodic insert logs, retry logs only within expected contention, all workers finished, and no failed messages for tested VFS/iteration combinations.
