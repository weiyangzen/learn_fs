# sources/sync-backup/git-lfs/tq/custom_test.go

Purpose: tests manifest registration of custom transfer adapters from Git config.

Important APIs/types/functions: `TestCustomTransferBasicConfig`, `TestCustomTransferDownloadConfig`, `TestCustomTransferUploadConfig`, and `TestCustomTransferBothConfig`.

Control flow: builds `lfsapi.Client` with config maps, creates a manifest, requests upload/download adapters, and asserts whether they are `*customAdapter` plus path/args/concurrent fields.

State and persistence: no durable state; client is closed after each test.

Dependencies and integration points: validates `configureCustomAdapters` and manifest adapter lookup behavior.

Risks: tests do not execute external adapter processes or standalone mode. One assertion assigns `cd, _ := u.(*customAdapter)` in the basic download block, which appears to inspect `u` rather than `d`.

Test signals: useful config coverage for direction and defaults.
