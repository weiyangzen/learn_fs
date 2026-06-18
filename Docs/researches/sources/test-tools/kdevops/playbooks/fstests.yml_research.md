# sources/test-tools/kdevops/playbooks/fstests.yml

Purpose: filesystem testing workflow entrypoint that prepares localhost result processing and runs fstests on baseline/dev.

Important APIs/types/functions: first play targets localhost with role `fstests_prep_localhost`; second play targets `baseline:dev` with role `fstests`.

Control flow: local preparation for JUnit/XML or result processing happens before remote fstests execution.

State/persistence behavior: creates local processing prerequisites and remote fstests work/result directories.

Dependencies/integration: driven by `KDEVOPS_WORKFLOW_ENABLE_FSTESTS` and role-specific Kconfig; integrates with filesystem baseline/regression workflows.

Risks/test signals: split local/remote setup means failures may appear later if local prep is skipped. Test signals are generated fstests results and local JUnit/XML processing artifacts.
