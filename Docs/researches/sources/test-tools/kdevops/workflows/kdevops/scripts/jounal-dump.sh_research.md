## sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-dump.sh

Purpose: Converts remote systemd journal files into artifact-friendly per-guest text dumps.

Important APIs/types/functions: Script inputs are one argument `DIR` pointing to remote journals and a hardcoded `hosts` inventory file. It uses `journalctl --file`.

Control flow: Creates a local `journal` directory, validates one argument, extracts guest names from the `[all]` group in `hosts`, then for each guest reads `$DIR/remote-$guest.journal` and writes `journal/$guest.journal` if present.

State and persistence: Persists text journal dumps under `journal/`. Reads remote journal binary files but does not alter them.

Dependencies and integration points: Depends on Ansible inventory format, systemd `journalctl`, and kdevops journal naming. The filename is misspelled `jounal`, matching related scripts.

Risks and test signals: Inventory parsing only reads immediate lines after `[all]` and may miss complex inventories. Test with a sample `hosts` file and one remote journal file.
