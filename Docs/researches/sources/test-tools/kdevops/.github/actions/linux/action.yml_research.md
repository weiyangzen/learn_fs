# sources/test-tools/kdevops/.github/actions/linux/action.yml

Purpose: composite GitHub Action that installs/builds the configured Linux kernel and records the resulting git reference for CI reporting.

Important APIs/types/functions: no inputs. Steps run `make linux`, then `cd linux/`, compute `git rev-parse --short=12 HEAD`, write it to `../ci.git_ref`, and echo it.

Control flow: delegate kernel checkout/build/boot work to `make linux`, then record the exact checked-out kernel commit after the `linux/` tree exists.

State/persistence behavior: mutates or creates the local `linux/` checkout and writes `ci.git_ref`.

Dependencies/integration: depends on workflow configuration from the configure action, kdevops Linux make targets, and `git` in the Linux checkout.

Risks/test signals: assumes `linux/` exists after `make linux`; if the make target succeeds without a checkout, metadata generation fails. Test signal is a valid 12-character commit hash in `ci.git_ref`.
