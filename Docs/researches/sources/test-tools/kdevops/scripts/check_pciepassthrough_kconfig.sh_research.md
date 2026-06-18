# sources/test-tools/kdevops/scripts/check_pciepassthrough_kconfig.sh

Purpose: checks whether a PCI passthrough Kconfig file exists.

Important APIs/types/functions: argument validation and tests for `Kconfig.<arg>` or `<arg>`.

Control flow: prints `n` for empty argument, `y` if either expected file path exists, otherwise `n`.

State/persistence behavior: read-only.

Dependencies/integration: Kconfig helper for optional PCI passthrough menus.

Risks/test signals: relative path depends on caller working directory. Test signal is `y` when config file exists.
