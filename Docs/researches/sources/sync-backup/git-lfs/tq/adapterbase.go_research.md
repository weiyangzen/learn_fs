# sources/sync-backup/git-lfs/tq/adapterbase.go

Purpose: shared worker-pool implementation for transfer adapters.

Important APIs/types/functions: `adapterBase`, `transferImplementation`, `newAdapterBase`, `Begin`, `Add`, `End`, `worker`, `newHTTPRequest`, `doHTTP`, `advanceCallbackProgress`, and `endpointURL`.

Control flow: `Begin` configures API client, remote, job channel, debug flags, starts N workers, and uses `authWait` so worker 0 prompts/authenticates before other workers proceed. `Add` sends jobs and closes a result channel after all are done. Workers validate size, call implementation `DoTransfer`, and emit `TransferResult`. HTTP helpers build action requests, optionally rewrite hrefs, attach headers, and choose authenticated/no-retry auth paths.

State and persistence: per-adapter job channel, wait groups, auth gate, callback, and API client state; no durable persistence.

Dependencies and integration points: embedded by basic, tus, SSH, and custom adapters; depends on `fs`, `lfsapi`, `errors`, `tr`, and `tracerx`.

Risks: `Begin` can return after some workers have already started if a later `WorkerStarting` fails. `Add` goroutine can block if `End`/worker lifecycle is misused. Auth gate correctness depends on implementations invoking `authOkFunc`.

Test signals: no direct adapterbase tests; behavior is indirectly covered through adapter/queue tests.
