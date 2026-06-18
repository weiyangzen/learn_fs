## sources/test-tools/kdevops/workflows/mmtests/Kconfig

Purpose: Configures mmtests repository and memory-management benchmark options.

Important APIs/types/functions: Symbols include `HAVE_MIRROR_MMTESTS`, `MMTESTS_GIT_URL`, `MMTESTS_TEST_TYPE`, `MMTESTS_ENABLE_THPCOMPACT`, `MMTESTS_ENABLE_THPCHALLENGE`, iteration/monitoring options, pretest drop-cache/compaction flags, and `MMTESTS_PRETEST_THP_SETTING`.

Control flow: The file is gated by `KDEVOPS_WORKFLOW_ENABLE_MMTESTS`, chooses repo URL from mirror/default, selects one mmtests type, sets iteration and monitor options, and sources type-specific and filesystem sub-Kconfigs.

State and persistence: Many symbols have `output yaml`, so selections become extra-vars. Runtime state is produced by Ansible/mmtests.

Dependencies and integration points: Integrates with libvirt mirror, default mmtests GitHub URL, monitoring playbooks, ftrace/proc/mpstat dependencies, and sourced mmtests subconfig files.

Risks and test signals: Monitor options assume target-side tool availability and permissions. Test by inspecting extra vars and running setup plus a small iteration count.
