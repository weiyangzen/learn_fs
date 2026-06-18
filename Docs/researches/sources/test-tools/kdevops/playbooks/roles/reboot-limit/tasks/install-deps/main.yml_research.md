<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/main.yml

Purpose: dispatches reboot-limit dependency installation by OS family.

Important APIs/types/functions: modules `ansible.builtin.import_tasks`; tasks `Reboot-limit distribution specific setup`.

Control flow: Includes Debian, RedHat, or Suse install task based on `ansible_os_family`.

State and persistence behavior: No direct state.

Dependencies and integration points: Called from reboot-limit main before loops.

Risks: Unsupported OS family gets no dependencies.

Test signals: Signals are expected include and later reboot task availability.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/main.yml -->
