# File Research: sources/virtualization/nvme-cli/tests/nvme_id_ns_test.py

Python integration test for Identify Namespace.

Flow:
- Collects namespace list via `nvme list-ns --output-format=json`.
- Runs `nvme id-ns <controller> --namespace-id=1`.
- Iterates every namespace from `nsid_list` and runs `id-ns`.
- Expects success for all.

Dependencies:
- Uses shared JSON parsing and namespace-list helpers from `TestNVMe`.
