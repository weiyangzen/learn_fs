# sources/test-tools/kdevops/.github/actions/cleanup/action.yml

Purpose: composite GitHub Action for final kdevops VM cleanup.

Important APIs/types/functions: no inputs. Single bash step runs `make destroy` with strict shell flags.

Control flow: invoked with `if: always()` in the main workflow to destroy guests even after failures.

State/persistence behavior: destroys external VM/provider state and may remove local generated state according to the make target.

Dependencies/integration: depends on the same kdevops configuration and provider tooling used for bringup.

Risks/test signals: cleanup failure can leave CI resources running. Test signal is a successful destroy target and no surviving CI-prefixed guests.
