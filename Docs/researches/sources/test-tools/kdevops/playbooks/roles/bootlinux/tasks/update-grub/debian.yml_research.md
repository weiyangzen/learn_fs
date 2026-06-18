# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/debian.yml

This Debian GRUB update file runs `update-grub` with privilege escalation, registers `grub_update`, and marks the task changed when the command exits successfully.

The important API is `ansible.builtin.command`; state persistence is the regenerated GRUB configuration under the distro's normal boot paths. Integration points are bootlinux main and install tasks that modify `/etc/default/grub`, install kernels, or set GRUB defaults. Risks include assuming `update-grub` exists, marking changed on every successful run, and no explicit stderr handling or retries. Test signals should include Debian/Ubuntu runs after kernel installation and validation that `/boot/grub/grub.cfg` contains the target kernel entry.
