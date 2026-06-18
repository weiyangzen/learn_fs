# File Research: sources/virtualization/guestfs-tools/inspector/example-windows.xml

Example `virt-inspector` XML for Windows Server 2012 Datacenter.

Contents:
- Root: `/dev/sda2`
- OS name/distro: `windows`
- Architecture: `x86_64`
- Product variant: `Server`
- Major/minor: `6.2`
- Windows fields: `windows_systemroot` and `windows_current_control_set`.
- Mountpoint: `/`
- Filesystem: NTFS with UUID.
- Drive mappings: `C` to `/dev/sda2`, `D` to `/dev/sda3`.
- Empty applications element.

Research relevance: documentation fixture for Windows-specific inspector fields and drive mapping output.
