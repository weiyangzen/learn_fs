# File Research: sources/virtualization/nvme-cli/tests/nvme_create_max_ns_test.py

Python integration test for creating the maximum advertised number of namespaces.

Flow:
- Skips if namespace management/attachment is unsupported.
- Computes per-namespace capacity from total NVM capacity divided by max namespace count, then halves it for headroom.
- Deletes all namespaces.
- Iterates from namespace ID 1 through `nn`, creating, attaching, and running one-block I/O on each namespace.
- Detaches and deletes every namespace, then resets controller.
- Tear down recreates namespace 1.

Risk:
- Highly destructive and potentially long-running on controllers with many namespace slots.
