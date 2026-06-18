# sources/test-tools/kdevops/.github/actions/archive/action.yml

Purpose: composite GitHub Action that collects and uploads kdevops CI results for archiving.

Important APIs/types/functions: inputs are optional `ci_workflow` defaulting to `demo` and required `ssh_private_key`. Steps use `webfactory/ssh-agent@v0.9.0`, run `make journal-dump`, run `make ci-archive CI_WORKFLOW=...`, and upload `archive/*.zip` with `actions/upload-artifact@v4`.

Control flow: start an SSH agent with the private key for the external results repository; dump systemd journals; build the archive zip via make; upload the generated zips as a workflow artifact named with the workflow id.

State/persistence behavior: produces local `archive/*.zip` and likely CI metadata/commit artifacts through the make target. It reads SSH private key secret but does not persist it itself.

Dependencies/integration: depends on kdevops make targets `journal-dump` and `ci-archive`, GitHub artifacts, and an SSH key with access to `linux-kdevops/kdevops-results-archive.git`.

Risks/test signals: missing secrets or archive files fail the action. `set -euxo pipefail` can expose command lines but not key contents from the action input. Test signal is a workflow run with a generated zip artifact and successful archive make target.
