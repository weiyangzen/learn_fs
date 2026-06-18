# File Research: sources/virtualization/nvme-cli/plugins/shannon/shannon-nvme.h

Shannon plugin registration header. It registers plugin name `shannon` with description `Shannon vendor specific extensions`.

Registered commands:
- `smart-log-add`
- `set-additioal-feature`
- `get-additional-feature`
- `id-ctrl`

The misspelling `set-additioal-feature` is part of the command surface and therefore externally visible.
