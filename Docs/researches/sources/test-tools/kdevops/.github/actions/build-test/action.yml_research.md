# sources/test-tools/kdevops/.github/actions/build-test/action.yml

Purpose: composite GitHub Action that installs or builds test suites required for a selected kdevops CI workflow.

Important APIs/types/functions: optional `ci_workflow` input defaulting to `demo`; single step runs `make ci-build-test CI_WORKFLOW=${{ inputs.ci_workflow }}`.

Control flow: delegates all workflow-specific test setup to the repository make target after configuration, bringup, and Linux install have completed.

State/persistence behavior: mutates guest or workspace state through the make target, such as installing fstests, blktests, or selftests dependencies.

Dependencies/integration: depends on `scripts/ci.Makefile`/workflow make plumbing and the selected `CI_WORKFLOW`.

Risks/test signals: lack of quoting around the substituted workflow is typical in actions but would be risky if input choices widened beyond controlled values. Test signal is a successful `ci-build-test` target before the test action runs.
