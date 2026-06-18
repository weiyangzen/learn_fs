# sources/test-tools/kdevops/playbooks/roles/update_etc_hosts/tasks/main.yml

Purpose: updates each target node's `/etc/hosts` with peer hosts and disables cloud-init host management when present.

Important APIs/types/functions: optional `include_vars`, `wait_for_connection`, `setup` network subset, `set_fact`, `stat`, `lineinfile`, `ansible.utils.ipaddr`, `hostvars`, and `ansible_play_hosts_all`.

Control flow: imports extra vars, waits for connectivity, gathers network facts, builds private network CIDR when enabled, builds peer-host list excluding current host, disables cloud-init management, writes peer host entries using private-network-filtered IPs or first IPv4 address, and fixes Debian guestfs unassigned-hostname line.

State/persistence behavior: mutates `/etc/cloud/cloud.cfg.d/99-kdevops-manage-net-disable` and `/etc/hosts` on target nodes.

Dependencies/integration: depends on inventory hostvars, network facts, `terraform_private_net_prefix/mask`, `ansible.utils` collection, NixOS/guestfs flags, and sudo.

Risks/test signals: `first` IP selection can pick the wrong interface; private-network filtering can fail if addresses are missing. Test signals are idempotent lineinfile output and resolvable peer hostnames.
