<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/main.yml

Purpose: dispatches pynfs dependency installation to Debian, RedHat, or Suse task files.

Important APIs/types/functions: modules `ansible.builtin.import_tasks`; tasks `Oscheck distribution ospecific setup`.

Control flow: Includes the OS-family-specific dependency file based on `ansible_os_family`.

State and persistence behavior: No direct persistent state.

Dependencies and integration points: Called from `pynfs/tasks/main.yml` before cloning/building pynfs.

Risks: Unsupported OS families receive no dependency setup.

Test signals: Test by running on each supported OS family and checking the expected include executes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/main.yml -->
