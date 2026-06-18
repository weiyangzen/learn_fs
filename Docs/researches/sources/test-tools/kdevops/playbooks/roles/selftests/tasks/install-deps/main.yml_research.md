<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main.yml

Purpose: dispatches target-side Linux selftests dependency installation by OS family.

Important APIs/types/functions: modules `ansible.builtin.import_tasks`; tasks `Oscheck distribution ospecific setup`.

Control flow: Includes Debian, RedHat, or Suse task files based on facts.

State and persistence behavior: No direct state.

Dependencies and integration points: Called at the start of `selftests/tasks/main.yml`.

Risks: Unsupported OS families skip dependency setup.

Test signals: Signals are expected include and subsequent selftests build readiness.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main.yml -->
