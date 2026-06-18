# sources/test-tools/syzkaller/syz-cluster/controller/main.go

Purpose: main process for syz-cluster controller service.

Important APIs/types/functions: `main`.

Control flow: creates app environment, starts `SeriesProcessor.Loop`, stats worker loop, and HTTP API server on port 8080 under an errgroup. Any returned error is fatal.

State and persistence: uses app environment repositories for Spanner/blob storage; HTTP server has no local persistence.

Dependencies and integration points: integrates `pkg/app`, controller API server, DB repositories, stats worker, and `SeriesProcessor`.

Risks: assumes one process instance; multiple replicas can race session processing. `http.ListenAndServe` error ends the app.

Test signals: covered indirectly by processor tests and controller test server utilities.
