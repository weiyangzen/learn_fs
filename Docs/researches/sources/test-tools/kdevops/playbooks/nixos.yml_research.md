# sources/test-tools/kdevops/playbooks/nixos.yml

Purpose: provisions and manages NixOS virtual machines for kdevops workflows through Nix-generated images, libvirt domains, and SSH configuration.

Important APIs/types/functions: eight plays cover dependency installation, config generation, disk image build/deploy, default libvirt network setup, VM provisioning, SSH access setup, access display, and destroy. It uses `nix`, `nix-build`, generated Nix templates, `virsh`, `openssh_keypair`, `slurp`, `set_fact`, `wait_for`, and helper scripts `nixos_ssh_key_name.py`, `check_nix_mirror.sh`, and `update_ssh_config_nixos.py`.

Control flow: install Nix/libvirt, create directories and SSH key, render NixOS configs and optional flakes, generate a qcow2 image through `make-disk-image.nix`, copy per-VM disks, render wrappers/XML, start libvirt domains, discover DHCP IPs, wait for SSH, update SSH config, and optionally destroy all generated VM artifacts under `destroy, never` tags.

State/persistence behavior: creates Nix store paths, `nixos_generation_dir`, `nixos_storage_dir`, qcow2 images, libvirt domains, VM XML files, wrapper scripts, SSH keys, and SSH config entries. Destroy removes many local artifacts and runs Nix garbage collection.

Dependencies/integration: integrates generated inventory groups, `extra_vars.yaml`, libvirt URI configuration, NixOS templates, local mirror detection, and kdevops SSH configuration.

Risks/test signals: there are duplicate task names for checking the disk image and waiting for SSH, which can obscure logs. Shell blocks are substantial and rely on Nix path/profile assumptions. Libvirt commands use `failed_when: false` in some critical places, so silent provisioning errors are possible. Test signals are built qcow2 path, active libvirt domains, discovered IPs, SSH reachability, generated SSH config entries, and successful destroy cleanup.
