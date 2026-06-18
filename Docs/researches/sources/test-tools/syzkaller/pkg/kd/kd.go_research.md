## sources/test-tools/syzkaller/pkg/kd/kd.go

Purpose: minimal Windows KD protocol decoder for extracting exception reports from debugger packets.

Important APIs/types/functions: `Decode`, packet header struct, constants, and KD payload structs `stateChange64`, `exception64`, `controlReport`.

Control flow: searches for the data header, waits for a full packet header and payload, skips incomplete data, and for 64-bit state-change packets formats a synthetic `BUG: first/second chance exception` report with payload details.

State and persistence: stateless byte-slice decoder.

Dependencies and integration: uses unsafe struct overlays and assumes little-endian host layout. Intended for VM output decoding.

Risks: unsafe casting from byte slices depends on alignment/layout/endian assumptions. Non-state-change packets are skipped silently. The returned `start` for no header keeps trailing bytes for future scans.

Test signals: `kd_test.go` decodes a canned exception packet.
