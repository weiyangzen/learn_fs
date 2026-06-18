<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pkg/tasks/debian.yml -->
# sources/test-tools/kdevops/playbooks/roles/pkg/tasks/debian.yml

Purpose: performs Debian-specific package manager setup for kdevops helper behavior.

Important APIs/types/functions: modules `ansible.builtin.set_fact`; variables/facts `is_bookworm`, `is_bullseye`, `is_buster`, `is_trixie`, `pkg_libaio`; tasks `Debian_libaio rename for buster`, `Debian_libaio rename for debian releases older than trixie`.

Control flow: Runs the task list in order, likely updating package metadata or installing base tools according to role defaults.

State and persistence behavior: Mutates apt/package state on Debian hosts.

Dependencies and integration points: Included only from `pkg/tasks/main.yml`.

Risks: Apt cache/network failures block downstream roles.

Test signals: Signals are idempotent apt task completion and availability of requested package helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pkg/tasks/debian.yml -->
