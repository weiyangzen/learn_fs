# sources/test-tools/kdevops/Kconfig

Purpose: root Kconfig menu for kdevops. It defines top-level project menu text, a few global config symbols, and includes the rest of the kdevops configuration tree.

Important APIs/types/functions: `mainmenu "$(PROJECT) $(PROJECTRELEASE)"`; config symbols `HAVE_KDEVOPS_CUSTOM_DEFAULTS`, `NEEDS_LOCAL_DEVELOPMENT_PATH`, `KDEVOPS_FIRST_RUN`, and `LOCAL_DEVELOPMENT_PATH`; `source` entries for defaults, distro, SSH, storage, git sources, email, hypervisor, mirror, bringup, sysctl, workflows, monitors, and kdevops options.

Control flow: Kconfig frontends load this file, expose "first run" and local development path prompts when dependencies match, and recursively include submenu files. `KDEVOPS_FIRST_RUN` uses `output yaml`, so selected values feed generated YAML configuration.

State/persistence behavior: selections are stored in `.config` and converted to `.extra_vars_auto.yaml` through kdevops kconfig tooling. `LOCAL_DEVELOPMENT_PATH` defaults to `$HOME/devel/` when local development is needed.

Dependencies/integration: used by `scripts/kconfig/kconfig.Makefile`, the top-level Makefile, defconfig targets, and YAML generation. Source paths must remain valid for menuconfig/oldconfig.

Risks/test signals: missing sourced Kconfig files break all configuration. Shell-derived defaults can vary by user environment. Test signals include `make oldconfig`, `make menuconfig`, and defconfig generation producing expected `.config` and YAML.
