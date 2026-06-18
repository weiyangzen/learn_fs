<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/defaults/main.yml

Source read: complete file, 66 lines, 2188 bytes, sha256 `9b9d5672ac7c6bd1`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/defaults/main.yml_research.md`.

Purpose: defaults for development host customization, repository setup, sysctl tuning, journal/timesync options, custom repos/packages, guestfs/source-copy behavior, and workflow flags.

Important APIs/types/functions: variables cover home/git/bash config paths, repo refresh/upgrade/kdevtools booleans, SUSE registration/KOTD/systemd watchdog settings, sysctl overcommit settings, RHEL org/activation, CLI install, journal remote, timesyncd/NTP provider choices, guestfs copy flags, Debian hop1 mirror tracking, unattended upgrades, inferred user/group, terraform/declared hosts, and custom repo/package comma-separated strings.

Control flow: no executable tasks; these defaults are consumed by multiple devconfig task files.

State and persistence behavior: defaults govern possible mutations to user dotfiles, package repositories, system update state, sysctl config, systemd services, package installs, and source copies.

Dependencies and integration: central variable surface for devconfig role, apt mirror repair, SUSE repo scripts, RedHat custom repos/packages, DataCrunch ML setup, guestfs, terraform, and workflow bootstrap.

Risks: many booleans default false, so feature tasks must explicitly enable them. Sensitive RHEL registration values default empty. Custom repo/package vars are strings requiring comma splitting and non-empty validation.

Test signals: role-level variable dump should confirm only intended devconfig features are enabled for a given inventory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/defaults/main.yml -->
