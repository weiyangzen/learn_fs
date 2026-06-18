# sources/test-tools/kdevops/requirements.yml

Purpose: Ansible Galaxy collection requirements for kdevops playbooks.

Important APIs/types/functions: declares `ansible.posix`, `ansible.utils`, `cloud.terraform`, `community.docker`, `community.general`, and `community.libvirt`.

Control flow: no runtime flow; consumed by `ansible-galaxy collection install`.

State/persistence behavior: installs collections into the Ansible collection path.

Dependencies/integration: required by roles using ipaddr filters, Terraform modules, Docker modules, LVM modules, and libvirt modules.

Risks/test signals: unpinned collection versions may drift. Test signals are collection install success and Ansible playbook syntax resolving modules.
