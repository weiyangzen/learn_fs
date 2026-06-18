# File Research: sources/virtualization/nvme-cli/nvme.spec.in

- Purpose: RPM spec template for packaging nvme-cli.
- Install behavior: runs `meson install`, creates host NQN/host ID placeholders under `@SYSCONFDIR@/nvme`, and packages binary, man pages, completions, config files, udev rules, dracut config, and systemd units.
- Post-install behavior: initializes hostnqn and hostid on first install if empty, reloads systemd, reloads udev rules, and triggers udev.
- Template variables: uses placeholders for version, license, URL, dependencies, install directories, and system paths.
