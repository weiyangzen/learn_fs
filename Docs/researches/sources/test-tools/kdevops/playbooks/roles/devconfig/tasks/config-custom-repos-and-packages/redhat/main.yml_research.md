<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/redhat/main.yml

Source read: complete file, 27 lines, 731 bytes, sha256 `5d54794d10ec1cf7`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/redhat/main.yml_research.md`.

Purpose: RedHat-family implementation for installing custom yum/dnf repository files and packages.

Important APIs/types/functions: `ansible.builtin.copy` copies each repo file to `/etc/yum.repos.d/{{ basename }}` with root ownership and 0644 mode; `ansible.builtin.dnf` installs each custom package with retries until rc 0. Inputs are comma-split `kdevops_devconfig_custom_repos` and `kdevops_devconfig_custom_packages`.

Control flow: if custom repos string length is greater than 1 after trim, iterate over comma-separated paths and copy them; if custom packages string length is greater than 1, iterate package names and dnf install with retry.

State and persistence behavior: writes repo files into `/etc/yum.repos.d` and mutates rpm package state.

Dependencies and integration: supports devconfig extensibility for RedHat-like images without changing core roles.

Risks: comma splitting has no whitespace cleanup per item, so values with spaces can fail. `copy src` reads from the controller, not target. Package task does not set `state: present` explicitly, relying on module default behavior.

Test signals: provide two repo files and packages with whitespace variations; verify copied basenames, dnf repo visibility, retry behavior, and idempotent second run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/config-custom-repos-and-packages/redhat/main.yml -->
