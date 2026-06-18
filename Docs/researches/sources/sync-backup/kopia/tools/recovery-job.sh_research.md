# sources/sync-backup/kopia/tools/recovery-job.sh

Purpose: orchestrates a Kopia recovery test job by building a Kopia binary, embedding source/test git metadata into robustness engine ldflags, and running the recovery test Make target in a separate recovery repository.

Control flow/APIs: required args are recovery repo directory, Kopia repo directory, test duration, test timeout, and repository path prefix. It logs selected environment variables, optionally displays local fio data directory usage, builds `kopia` from the Kopia repo, gathers git revision/branch/dirty/build-time metadata from both repos, constructs `-ldflags`, and invokes `make -C "$kopia_recovery_dir" KOPIA_EXE=... GO_TEST='go test' TEST_FLAGS=... recovery-tests`.

State/persistence: writes the built Kopia executable into the Kopia repo directory. The invoked Make target likely writes test/recovery state under the provided repository path prefix and fio data paths.

Dependencies/integration: requires bash, Go, Git, Make, and environment credentials for S3-backed repositories when used. It integrates Kopia's executable with the robustness/recovery test harness under `tests/robustness/engine`.

Risks/test signals: no trap restores directories after partial failure, though `pushd/popd` are used. Quoting inside `TEST_FLAGS` is fragile due embedded `-ldflags` string. It prints presence of secret variables but masks `AWS_SECRET_ACCESS_KEY`. The recovery Make target's success is the signal.
