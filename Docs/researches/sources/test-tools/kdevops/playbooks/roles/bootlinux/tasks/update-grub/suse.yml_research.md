# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/suse.yml

This SUSE GRUB update file runs `update-bootloader --refresh` with privilege escalation, registers `grub_update`, and marks the task changed when the command succeeds.

The important API is privileged `ansible.builtin.command`. Persistent state is the refreshed SUSE bootloader configuration. Integration points are bootlinux kernel install/uninstall flows and any prior edits to GRUB defaults. Risks include assuming `update-bootloader` exists on all SUSE variants, changed-on-success behavior, and no validation that the intended kernel entry was produced or selected. Test signals should include SLE/openSUSE kernel install runs followed by bootloader menu inspection and reboot verification.
