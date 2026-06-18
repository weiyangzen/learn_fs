<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/main.yml

Source read: complete file, 22 lines, 794 bytes, sha256 `479b00a197f3d129`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/main.yml_research.md`.

Purpose: OS and distribution dispatcher for QEMU build dependencies.

Important APIs/types/functions: optional `include_vars` loads `{{ ansible_facts['os_family'] | lower }}.yml`; `import_tasks` dispatches to Debian, SUSE, RedHat, or Fedora task files.

Control flow: load optional distribution-specific variables if present; run Debian for Debian family, SUSE for SUSE family, RedHat for RedHat family except Fedora, and Fedora for Fedora distribution.

State and persistence behavior: no direct state changes except loaded vars; imported files install package dependencies.

Dependencies and integration: called from `build_qemu/tasks/main.yml` only when a QEMU source build is requested and needed.

Risks: RedHat package file appears to use Debian-style package names in places, making the Fedora split important and non-Fedora RedHat behavior suspect. Unsupported distributions silently skip dependency setup.

Test signals: syntax check and dry runs should prove only one install-deps path is selected; Fedora must not also run `redhat/main.yml`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_qemu/tasks/install-deps/main.yml -->
