# sources/storage-engines/badger/.github/workflows/ci-badger-bank-tests-nightly.yml

Purpose: scheduled and push-triggered stress CI for the Badger bank workload.

Important flow: it runs on `main` and `release/v*` pushes plus a daily cron. The job checks out code, sets up Go from `go.mod`, installs system dependencies and jemalloc, installs the Badger CLI with race detector and jemalloc tags, generates a random key file, and runs `badger bank test` for four hours with encryption. Failure handling distinguishes data-race logs from transaction invariant failures and invokes `badger bank disect` with the decryption key path for diagnosis.

State and persistence: CI writes temporary DB files, key file, and `badgerbanktest.log`; no artifacts are uploaded here. Dependencies are Badger CLI, jemalloc, race builds, and shell utilities. Risks: long duration can consume runner budget, grep filtering around `Moved $5` drives status logic, and the encryption key is stored in a file in the workspace. Test signals are nightly pass/fail, race detector output, and dissection output on invariant failure.
