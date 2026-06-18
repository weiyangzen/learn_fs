# File Research: sources/virtualization/nvme-cli/tests/nvme_format_test.py

Python integration test for namespace formats.

Flow:
- Skips if namespace management/attachment is unsupported.
- Creates a small primary namespace, attaches it, reads `id-ns --output-format=json`, and captures `lbafs`.
- Detaches/deletes namespace and resets controller.
- Iterates every advertised LBA format, creates namespace 1 with that format, attaches it, runs I/O, detaches, deletes, and resets.
- Uses `dps=1` when metadata size string equals `8`, otherwise `0`.
- Tear down recreates namespace 1.

Risk:
- Destructive and format-changing by design.
