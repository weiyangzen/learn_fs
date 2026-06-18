# sources/security-integrity/ecryptfs-utils/src/libecryptfs/messaging.c

## Purpose
Provides shared packet-length encoding/decoding and a small abstraction over eCryptfs kernel messaging backends. The only active backend is the misc device interface; netlink is explicitly unsupported.

## Important APIs, types, and functions
- `ecryptfs_write_packet_length` encodes OpenPGP-style one- or two-byte packet lengths for sizes below 65536.
- `ecryptfs_parse_packet_length` decodes one- and two-byte lengths and rejects five-byte or invalid encodings.
- `ecryptfs_init_messaging`, `ecryptfs_messaging_exit`, `ecryptfs_send_message`, and `ecryptfs_run_daemon` dispatch to miscdev support.

## Control flow
Length encoding selects one byte for sizes below 192, two bytes for sizes below 65536, and rejects larger sizes. Messaging initialization switches on requested type and delegates miscdev setup. Send and daemon operations switch on the stored context type and call `miscdev.c`.

## State and persistence behavior
Stores backend type and file descriptor state inside `struct ecryptfs_messaging_ctx`. It does not persist data; actual kernel communication and descriptor lifecycle are delegated to miscdev helpers.

## Dependencies and integration points
Used by `packets.c` and `miscdev.c` for message framing. It depends on shared message constants and structs from `ecryptfs.h`.

## Risks and edge cases
The packet length implementation does not support five-byte lengths, so larger payloads fail. `ecryptfs_parse_packet_length` assumes enough input bytes are available for the indicated encoding; callers must bounds-check the containing buffer. The abstraction still exposes netlink constants even though the path is unsupported, so callers must handle `-EINVAL`.

## Test signals
Unit tests should cover boundary sizes 0, 191, 192, 65535, and 65536; reject first-byte 255 and invalid encodings; and verify miscdev initialization/send/run dispatch returns `-EINVAL` for unsupported types.
