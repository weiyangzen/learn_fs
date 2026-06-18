# File Research: sources/virtualization/nvme-cli/tests/nvme_get_features_test.py

Python integration test for mandatory Get Features IDs.

Flow:
- Tests feature IDs `0x01`, `0x02`, `0x04`, `0x05`, `0x07`, `0x08`, `0x09`, `0x0A`, and `0x0B`.
- Determines interrupt vector count by grepping `/proc/interrupts` for controller queue names.
- For Interrupt Vector Configuration (`0x09`), loops over detected vectors and passes `--cdw11`.
- For Error Recovery (`0x05`), includes namespace ID.
- Uses `--human-readable` for all feature commands.

Dependencies:
- Requires Linux `/proc/interrupts` layout and controller queue naming.
