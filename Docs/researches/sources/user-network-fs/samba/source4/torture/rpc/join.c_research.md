# sources/user-network-fs/samba/source4/torture/rpc/join.c

## Purpose
This file implements `torture_rpc_join()`, a helper-style RPC torture test for joining a domain with temporary machine accounts and verifying those credentials can connect to `IPC$`.

## Important APIs, Types, And Functions
The function uses `torture_join_domain()` and `torture_leave_domain()` to create and remove test accounts named `smbtorturejoin`. It uses `smbcli_full_connection()` to connect to the target host's `IPC$` share with the generated machine credentials. It reads the target host from the `host` torture setting and obtains SMB client/session options from loadparm.

## Control Flow
The test first joins as a member workstation using `ACB_WSTRUST`, connects to `IPC$`, disconnects, and leaves the domain. It then repeats the flow as a domain-controller-style trust account using `ACB_SVRTRUST`. Any join or IPC connection failure returns false.

## State And Persistence Behavior
The function creates domain machine accounts and removes them after each phase. If the IPC connection fails after a successful join, the code returns false before calling `torture_leave_domain()`, so stale `smbtorturejoin` accounts may remain. Successful paths disconnect the SMB tree and leave the domain.

## Dependencies And Integration Points
Dependencies include Samba torture domain-join helpers, credential generation, SMB client connection APIs, name resolution, socket options, session options, event loop, and gensec settings. It integrates with directory/account management and IPC$ authentication paths.

## Risks And Edge Cases
The fixed NetBIOS name can collide with stale accounts or parallel test runs. Cleanup is not protected by a common failure path, so connection failures after join leak domain state. The debug message for the second phase still says workstation credentials, although the account type is server trust.

## Test Signals
Success requires both account types to join, authenticate to `IPC$`, disconnect, and leave the domain. Failure signals are null `test_join` returns or non-OK `smbcli_full_connection()` statuses.
