# File Research: sources/virtualization/nvme-cli/tests/nvme_copy_test.py

Python integration tests for NVMe Copy descriptor formats.

Structure:
- `TestNVMeCopy`: shared base for copy tests.
- `TestNVMeCopyFormat0`: in-namespace copy with descriptor format 0.
- `TestNVMeCopyFormat1`: in-namespace copy with descriptor format 1 after reformatting to 64-bit guard PI.
- `TestNVMeCopyFormat23`: cross-namespace copy with descriptor formats 2 and 3, including `sopts` variants.

Key behaviors:
- Reads Optional Copy Formats Supported (`ocfs`) and namespace copy limits (`mcl`, `mssrl`, `msrc`).
- Skips unsupported descriptor formats or namespaces with zero copy limits.
- Detects current PIF from `id-ns` and `nvm-id-ns`.
- Can recreate namespace 1 with a chosen LBA format when namespace management is supported.
- Enables Host Behavior Support CDFE bits for cross-namespace descriptor formats and restores the original CDFE in teardown.
- Runs `nvme copy` with destination LBA, source block list, descriptor format, optional source namespace ID, and optional source options.

Risk:
- Can reformat/delete/recreate namespaces for 64-bit guard copy tests.
