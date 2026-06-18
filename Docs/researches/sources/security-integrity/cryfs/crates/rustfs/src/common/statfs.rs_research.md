# sources/security-integrity/cryfs/crates/rustfs/src/common/statfs.rs

Purpose: filesystem capacity and capability statistics.

Important APIs: `Statfs` fields include total/free/available blocks and files, block size, max filename length, and fragment size.

Control flow and state: plain data returned by `statfs`.

Dependencies and integration: object `Device::statfs`, high-level `AsyncFilesystem::statfs`, and low-level `AsyncFilesystemLL::statfs` use this shared struct.

Risks and tests: no validation of consistency between block counts and sizes. Backends must map it correctly to FUSE statfs replies.
