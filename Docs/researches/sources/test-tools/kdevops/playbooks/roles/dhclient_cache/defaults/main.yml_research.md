# sources/test-tools/kdevops/playbooks/roles/dhclient_cache/defaults/main.yml

## Purpose
Defines default variables for the `dhclient_cache` role, which adds DHCP lease persistence hooks so cloud VMs retain usable network configuration across transient DHCP or reboot races. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `dhclient_cache` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated after networking is present but before long test runs. It relies on `/etc/dhcp`, `/etc/NetworkManager/dispatcher.d`, `/etc/wicked/extensions`, per-interface facts, and lease-cache templates.

## Risks
The main risk is installing hooks for the wrong DHCP stack or interface, which can preserve stale addresses or fail to update cache files after network changes. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
