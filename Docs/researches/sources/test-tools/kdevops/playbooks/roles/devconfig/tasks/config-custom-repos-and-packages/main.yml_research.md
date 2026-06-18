<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/main.yml

Source read: complete file, 6 lines, 194 bytes, sha256 `b2b019b08a5390bc`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/main.yml_research.md`.

Purpose: dispatcher for custom repository and package installation tasks in devconfig.

Important APIs/types/functions: `ansible.builtin.import_tasks: redhat/main.yml` gated by `ansible_facts['os_family']|lower == 'redhat'`.

Control flow: only RedHat-family hosts run custom repo/package setup.

State and persistence behavior: no direct mutation; imported task copies repo files and installs packages.

Dependencies and integration: called by devconfig when custom repo/package variables are configured.

Risks: Debian/SUSE custom repo/package vars are ignored by this dispatcher. Static import can expose syntax errors even when skipped.

Test signals: RedHat dry run should include copy/dnf tasks when variables are non-empty; non-RedHat should skip.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/main.yml -->
