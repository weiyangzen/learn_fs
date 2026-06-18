# sources/test-tools/syzkaller/tools/syz-db-export/reprolist.go

Purpose: this dashboard export helper downloads public or authenticated syzbot bug metadata and one C reproducer per bug into an on-disk export tree. It is configured by dashboard URL, namespace, access level, bearer token, output directory, parallelism, and verbosity flags.

Important APIs and flow: `main` creates the output directory, validates namespace, and calls `exportNamespace`. `exportNamespace` uses `dashboard/api.Client`, fetches open and fixed bug groups, starts `errgroup` workers, and feeds bug indexes through a channel. Each worker loads full bug details, calls `saveBug`, checks the first crash's `CReproducerLink`, downloads text with `cli.Text`, extracts the repro ID through `reproIDFromURL`, and writes it with `saveCRepro`. `saveBug` marshals `api.Bug` to JSON and writes `bugs/<bugID>/details.json`; `saveCRepro` writes `bugs/<bugID>/<reproID>.c`.

State and persistence: all durable state is the export directory. There is no resume manifest or deduplication; reruns overwrite details and C reproducer files with mode `0666`. Parallel workers share the same dashboard client and output root but operate per bug directory.

Dependencies and integration: depends on `dashboard/api`, `errgroup`, JSON marshaling, and filesystem writes. It is an offline corpus/dashboard-data collection utility, not a manager runtime component.

Risks: `reproIDFromURL` assumes exactly one `&` and one `=` in the URL tail and panics otherwise. `bug.Crashes[0]` assumes every returned bug has at least one crash. Worker cancellation is limited; the feeder selects on one error channel but then calls `g.Wait` again. File permissions are broad and writes are not atomic.

Test signals: no direct test file is assigned. Useful future tests would mock `api.Client` responses, malformed repro URLs, bugs without crashes, and parallel export errors.
