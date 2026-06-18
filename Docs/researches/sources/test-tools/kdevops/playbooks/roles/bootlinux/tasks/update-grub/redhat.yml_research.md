# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/redhat.yml

This Red Hat GRUB update file disables GRUB menu auto-hide, detects UEFI by checking `/sys/firmware/efi/efivars`, sets `grub_config_file` to `/etc/grub2.cfg` for BIOS or `/etc/grub2-efi.cfg` for UEFI, then runs `grub2-mkconfig -o` against that path.

Important APIs are privileged `command`, `stat`, `set_fact`, and changed-state registration. Persistent state includes GRUB environment and regenerated GRUB config files. Integration points are Red Hat bootlinux kernel install/uninstall flows and saved-default handling in other tasks. Risks include `grub2-editenv - unset menu_auto_hide` missing `changed_when`, assumptions about `/etc/grub2*.cfg` symlink locations, and marking every successful mkconfig as changed. Test signals should include BIOS and UEFI Red Hat family hosts and validation that the target kernel appears in the generated menu.
