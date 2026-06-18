# sources/test-tools/kdevops/.github/actions/bringup/action.yml

Purpose: composite GitHub Action that resets and brings up kdevops guests.

Important APIs/types/functions: has no inputs. Single bash step runs `make destroy` followed by `make bringup` with `set -euxo pipefail`.

Control flow: destroy any existing VM state first, then create/provision guests through the repository make targets.

State/persistence behavior: intentionally mutates external virtualization state by destroying and recreating guests. It also updates generated local state produced by bringup.

Dependencies/integration: depends on configured `.config`, generated inventory/vars, hypervisor/provider tooling, and kdevops make targets.

Risks/test signals: `make destroy` is destructive and runs unconditionally, so this action is only appropriate for disposable CI host prefixes. Test signals are successful guest creation, reachable inventory, and cleanup later in the workflow.
