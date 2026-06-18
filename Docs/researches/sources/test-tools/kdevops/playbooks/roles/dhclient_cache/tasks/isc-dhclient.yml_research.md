# sources/test-tools/kdevops/playbooks/roles/dhclient_cache/tasks/isc-dhclient.yml

## Purpose
Main task orchestration for the `dhclient_cache` role, which adds DHCP lease persistence hooks so cloud VMs retain usable network configuration across transient DHCP or reboot races. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Detect primary network interface`, `Create dhclient enter hook for persistent lease caching`, `Create dhclient exit hook for persistent lease caching`, `Update dhclient configuration for aggressive retry`, `Ensure lease cache directory exists`, `Create initial cached lease from current lease`. Important modules/directives include `args`, `become`, `become_flags`, `become_method`, `create`, `creates`, `dest`, `file`, `group`, `line`, `lineinfile`, `loop`; plus 10 more. Key variable inputs observed in this file include `ansible_default_ipv4`, `dhclient_cache_retry_interval`, `dhclient_cache_timeout`, `item`, `primary_interface`. The role-level integration surface is the `dhclient_cache` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Detect primary network interface`, `Create dhclient enter hook for persistent lease caching`, `Create dhclient exit hook for persistent lease caching`, `Update dhclient configuration for aggressive retry`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `template`, `file`, `lineinfile`. Notable path references include `/CentOS/Fedora`, `/etc/dhcp/dhclient-enter-hooks.d/kdevops-persistent-cache`, `/etc/dhcp/dhclient-exit-hooks.d/kdevops-persistent-cache`, `/etc/dhcp/dhclient.conf`, `/var/lib/dhcp/cache`, `/var/lib/dhcp/cache/dhclient.{{`, `/var/lib/dhcp/dhclient.{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after networking is present but before long test runs. It relies on `/etc/dhcp`, `/etc/NetworkManager/dispatcher.d`, `/etc/wicked/extensions`, per-interface facts, and lease-cache templates. Shell/command integration points observed here include `|`.

## Risks
The main risk is installing hooks for the wrong DHCP stack or interface, which can preserve stale addresses or fail to update cache files after network changes. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
