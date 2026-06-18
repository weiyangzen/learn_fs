# File Research: sources/virtualization/nvme-cli/plugins/meson.build

This top-level plugin Meson file maps selected nvme-cli plugin names to source files and conditionally enters multi-file plugin subdirectories.

Main behavior:
- Defines `all_plugins`, mapping plugin names to C source files for simple plugins.
- Includes the group’s simple plugins:
  - `innogrit`: `plugins/innogrit/innogrit-nvme.c`
  - `inspur`: `plugins/inspur/inspur-nvme.c`
  - `intel`: `plugins/intel/intel-nvme.c`
  - `mangoboost`: `plugins/mangoboost/mangoboost-nvme.c`
  - `memblaze`: `plugins/memblaze/memblaze-nvme.c`
- On non-Windows hosts, reads selected plugin names from Meson option `plugins`; on Windows, selects none.
- Builds `plugin_sources` by stripping selected plugin names and appending matching entries from `all_plugins`.
- Conditionally adds subdirectories:
  - `feat`
  - `lm`
  - `ocp`
  - `sed` when OPAL support is enabled
  - `solidigm` when json-c is available
- Also conditionally includes `nbft` when fabrics support and `nbft` selection are present.

Role:
- This is the central build selection layer for nvme-cli plugins. LM is not in `all_plugins` because it has its own `plugins/lm/meson.build`.
