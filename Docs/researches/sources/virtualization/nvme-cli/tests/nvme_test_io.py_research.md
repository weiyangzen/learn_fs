# File Research: sources/virtualization/nvme-cli/tests/nvme_test_io.py

Shared read/write helper subclass for Python tests.

Key elements:
- Determines active data size, metadata size, PI type, metadata transfer mode, and `prinfo`.
- Handles three major cases:
  - PI active with extended LBA: uses `prinfo=8` so controller inserts/strips PI.
  - PI active with separate metadata: uses `prinfo=0` and explicit zero metadata buffers.
  - No PI: includes metadata bytes in data size only for extended LBA mode.
- Provides data-file creation with repeated text pattern.
- Provides binary zero metadata file creation.
- Builds `nvme write` and `nvme read` commands with data, optional `--prinfo`, and optional metadata file arguments.

Role:
- Keeps data/metadata/PI command construction consistent across compare, read/write, write-zeroes, and write-uncorrectable tests.
