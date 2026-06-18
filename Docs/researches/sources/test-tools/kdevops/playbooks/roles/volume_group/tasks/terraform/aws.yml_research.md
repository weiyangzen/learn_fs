# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/aws.yml

Purpose: discovers AWS EBS devices attached for kdevops as LVM candidates.

Important APIs/types/functions: `find` under `/dev/disk/kdevops` and `set_fact` extracting link paths.

Control flow: finds symlinks excluding the data device basename, then sets `physical_volumes` to those paths.

State/persistence behavior: only Ansible fact mutation; no disk writes here.

Dependencies/integration: relies on a udev rule creating stable `/dev/disk/kdevops` links for EBS volumes.

Risks/test signals: missing udev links or incorrect data-device exclusion can select wrong volumes. Test signal is stable repeatable `physical_volumes` list.
