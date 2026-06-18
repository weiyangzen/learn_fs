# sources/test-tools/crashmonkey/vm_scripts/clone_vms.sh

Purpose: clones a base VirtualBox VM `ubuntu16-vm1` into a numbered range and assigns incrementing NAT SSH port forwards.

Important APIs/types/functions: args `start`, `end`, `port`, `VBoxManage clonevm`, `modifyvm --natpf1 delete ssh`, and `modifyvm --natpf1 "ssh,tcp,,<port>,,22"`.

Control flow: validates three args, loops from start to end, clones/registers each VM, replaces the `ssh` NAT rule, then increments port. State/persistence behavior: creates registered VirtualBox VMs and mutates their NAT configuration.

Dependencies/integration: used by `setup.sh` after importing a base OVA. Risks/test signals: assumes base VM and rule name exist, does not stop on individual VBoxManage failure, and can leave partially configured clones.
