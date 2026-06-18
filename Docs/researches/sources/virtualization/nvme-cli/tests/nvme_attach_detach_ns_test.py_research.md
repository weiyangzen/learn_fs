# File Research: sources/virtualization/nvme-cli/tests/nvme_attach_detach_ns_test.py

Python integration test for namespace create/attach/detach/delete.

Flow:
- Inherits `TestNVMe`.
- Skips if namespace management/attachment is unsupported.
- Computes namespace size from controller NVM capacity and active LBA format.
- Deletes all namespaces in setup.
- Creates namespace 1, attaches it, runs simple I/O, detaches it, deletes it, and resets the controller.
- Tear down recreates and attaches the primary namespace.

Risk:
- Destructive by design: deletes namespaces on the configured controller.
