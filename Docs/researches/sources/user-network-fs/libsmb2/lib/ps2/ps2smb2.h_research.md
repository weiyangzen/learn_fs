<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/ps2smb2.h -->
# sources/user-network-fs/libsmb2/lib/ps2/ps2smb2.h

## Purpose

`ps2smb2.h` defines the PS2-facing SMB2MAN devctl command contract and small data structures used to connect and disconnect SMB shares through the `smb:` IOP filesystem device.

## Important APIs, Types, And Functions

The header exports `SMB2_PATH_MAX`, devctl command constants `SMB2_DEVCTL_CONNECT` and `SMB2_DEVCTL_DISCONNECT_ALL`, `SMB2_MAX_NAME_LEN`, and structs `smb2Connect_in_t`, `smb2Connect_out_t`, and `smb2Disconnect_in_t`. Connect input carries a local share name, username, password, and SMB URL. Connect and disconnect outputs/inputs pass raw context pointers.

## Control Flow

There is no executable flow. Runtime flow is provided by `SMB2_devctl` in `smb2_fio.c`, which switches on these command IDs and consumes the structs.

## State And Persistence Behavior

The header defines ABI layout only. Runtime state behind `ctx` pointers is owned by the SMB2MAN driver and libsmb2 contexts; no persistent storage is defined.

## Dependencies And Integration Points

It integrates PS2 EE/IOP callers with the IOP driver. Callers must populate fixed-size character arrays and issue devctl to device `smb:`. `smb2_fio.c` uses `SMB2_MAX_NAME_LEN` for its mounted-share list.

## Risks And Edge Cases

Fixed-size credentials and URL buffers can truncate if callers do not validate lengths before copying. The disconnect-all command is defined but not implemented in the observed `SMB2_devctl`, and `smb2Disconnect_in_t` is not consumed there. Passing raw context pointers across the interface creates lifetime and trust risks.

## Test Signals

Test ABI sizes on the PS2 toolchain, connect calls with maximum field lengths, unsupported devctl handling, and future disconnect command behavior if implemented.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/ps2smb2.h -->
