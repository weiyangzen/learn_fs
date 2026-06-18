# File Research: sources/virtualization/nvme-cli/nvmf-autoconnect/dracut-conf/70-nvmf-autoconnect.conf.in

- Purpose: dracut configuration snippet.
- Behavior: adds the generated `70-nvmf-autoconnect.rules` udev rule to initramfs install items through `install_items+=`.
