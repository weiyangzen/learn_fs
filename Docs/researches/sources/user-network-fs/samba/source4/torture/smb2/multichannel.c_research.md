# sources/user-network-fs/samba/source4/torture/smb2/multichannel.c

## Purpose
`multichannel.c` tests SMB3 multichannel negotiation, channel binding, network-interface discovery, oplock/lease break routing across bound transports, channel retry behavior under blocked transports, maximum channel limits, and a channel-merging race regression.

## Important APIs, Types, and Functions
The suite entry point is `torture_smb2_multichannel_init()`, which creates `generic`, `oplocks`, `leases`, and `bugs` subsuites. `test_ioctl_network_interface_info()` sends `FSCTL_QUERY_NETWORK_INTERFACE_INFO` and decodes `fsctl_net_iface_info`. `test_multichannel_create_channel()` connects a transport and optionally binds it to a parent session using `smb2_session_channel()` and `smb2_session_setup_spnego()`, installs oplock and lease handlers, and sends keepalive so async break handling is active. `test_multichannel_create_channel_array()` and `test_multichannel_create_channels()` build channel sets sharing a client GUID.

Oplock tests cover basic break delivery, retry when the break channel is blocked, and two 32-channel models: observed Windows behavior where only the latest channel is used and specification behavior where breaks are attempted across channels. Lease tests mirror basic/retry/cross-channel-ack cases and a V2 epoch/order test over 32 blocked channels. `test_multichannel_num_channels()` checks the Windows-style 32-channel limit. `test_multichannel_bug_15346()` opens 31 raw SMB connections, negotiates them concurrently, verifies echo, then binds each as a session channel and runs a root getinfo.

## Control Flow
Each behavioral test first checks SMB3 dialect, `SMB2_CAP_MULTI_CHANNEL`, and interface info support. It then creates `multichanneltestdir`, opens files with leases or oplocks on secondary channels, opens conflicting handles from the primary session, and inspects which transport received a break. Blocking helpers from `block.h` simulate unresponsive channels so retry and timeout behavior can be observed. Break handler state is reset between phases to isolate counts. Cleanup restores the original primary session pointer, closes handles on the right tree, unlinks files, deletes the base directory, unblocks transports, and frees channel trees.

## State and Persistence Behavior
Persistent server state is limited to temporary files/directories and server-side open/lease/oplock/channel state. Client-side state includes arrays of `smb2_tree` pointers, per-channel timing structures, global `break_info` and `lease_break_info`, blocked transport state, and async `tevent_req` objects for the bug regression. Durable V2 create fields are initialized in helper routines but the tests assert Samba currently reports non-durable opens in these scenarios.

## Dependencies and Integration Points
The file integrates many Samba subsystems: SMB2 connect/session/channel APIs, ioctl/NDR decoding, credentials and loadparm configuration, resolver/socket helpers, `smbXcli` negotiation/echo, security definitions, oplock and lease break handlers, and transport-blocking test utilities. It relies on `oplock_break_handler.h` and `lease_break_handler.h` for shared callback state.

## Risks and Edge Cases
The tests intentionally distinguish Samba, Windows, and specification behavior, so some expectations are split into separate subtests. Timing-sensitive checks require break retries or opens to take more than 35 seconds when channels are blocked, which can make the suite slow and environment-sensitive. The same global break state is reused across many channels and must be reset carefully. Several cleanup blocks close handles through specific secondary trees; incorrect tree selection can mask routing bugs or cause noisy cleanup statuses. Channel count expectations assume a 32-channel server limit.

## Test Signals
Signals include SMB3/multichannel capability skips, decoded interface info, successful channel binding, local TCP port diagnostics, break counts and receiving transports, lease epoch increments, ordered per-channel break numbers, open durations under blocked transports, expected `NT_STATUS_INSUFFICIENT_RESOURCES` for channel 33, echo/getinfo success after concurrent negotiation, and absence of assertion flags in the bug 15346 async state.
