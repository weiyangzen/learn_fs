# File Research: sources/virtualization/nvme-cli/.github/workflows/libnvme-cleanup-python.yml

- Purpose: manual cleanup of libnvme development releases on TestPyPI.
- Inputs: `keep-last` defaults to 5; `dry-run` defaults to true.
- Key behavior: installs `pypi-cleanup`, enters `libnvme`, and deletes versions matching `.*\.dev[0-9]+` from TestPyPI unless dry-run is selected.
- Secret: uses `TEST_PYPI_API_TOKEN`.
