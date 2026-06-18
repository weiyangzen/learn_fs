# sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/wicked.yml

## Purpose
Main task orchestration for the `dhclient_cache` role, which adds DHCP lease persistence hooks so cloud VMs retain usable network configuration across transient DHCP or reboot races. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Detect primary network interface`, `Create wicked extension for DHCP cache save`, `Ensure lease cache directory exists`, `Get current IP configuration via wicked`. Important modules/directives include `args`, `become`, `become_flags`, `become_method`, `changed_when`, `creates`, `dest`, `file`, `group`, `mode`, `owner`, `path`; plus 6 more. Key variable inputs observed in this file include `ansible_default_ipv4`, `primary_interface`. The role-level integration surface is the `dhclient_cache` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Detect primary network interface`, `Create wicked extension for DHCP cache save`, `Ensure lease cache directory exists`, `Get current IP configuration via wicked`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `template`, `file`. Notable path references include `/etc/wicked/extensions/kdevops-dhcp-cache`, `/var/lib/wicked/cache`, `/var/lib/wicked/cache/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after networking is present but before long test runs. It relies on `/etc/dhcp`, `/etc/NetworkManager/dispatcher.d`, `/etc/wicked/extensions`, per-interface facts, and lease-cache templates. Shell/command integration points observed here include `|`.

## Risks
The main risk is installing hooks for the wrong DHCP stack or interface, which can preserve stale addresses or fail to update cache files after network changes. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
