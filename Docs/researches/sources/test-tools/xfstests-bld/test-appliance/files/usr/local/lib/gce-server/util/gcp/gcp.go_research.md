# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/gcp.go

Purpose: shared Google Cloud Platform wrapper for Compute Engine instance operations, quota discovery, and Cloud Storage object management.

Important types/APIs: `Service` owns context, compute service, and optional storage bucket; `Quota` stores zone-level CPU/IP/SSD shard capacity. APIs include `NewService`, `Close`, instance metadata/get/delete/reset/start, region and zone quota lookup, `GetMaxShard`, storage listing/deletion/upload, and `NotFound`.

Control flow: `NewService` uses application default credentials with Cloud Platform scope, creates Compute and Storage clients, and validates the bucket if supplied. Quota calculation chooses an UP zone in a region and computes shard capacity from available CPUs/2, IPs, and SSD GB divided by `max(50, GCE_MIN_SCR_SIZE)`. Storage helpers list by prefix, delete all matched objects, or upload one local file.

State and dependencies: external GCP resources and context cancellation. Depends on Google Cloud Go storage, compute API, oauth default credentials, and config for scratch disk sizing.

Risks and test signals: quota uses regional quota and one chosen zone, which may not reflect per-zone machine availability. `UploadFile` name says file or directory but only opens files. Delete-by-prefix can remove broad object sets if callers pass bad prefixes. Tests should mock GCP clients; current code has no unit tests here.
