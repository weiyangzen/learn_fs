# File Research: sources/virtualization/nvme-cli/plugin.h

- Purpose: lightweight declarations for the nvme-cli plugin framework.
- Structures: defines `program`, `plugin`, and `command` with command arrays, parent/next/tail links, names, versions, descriptions, handlers, and aliases.
- API: declares `general_help()` and `handle_plugin()`.
