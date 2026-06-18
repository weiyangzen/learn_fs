# sources/user-network-fs/samba/source4/smb_server/smb/signing.c

## Purpose
Provides SMB1 signing setup, incoming signature validation, outgoing signature generation, and sequence-number bookkeeping for normal replies and no-reply commands.

## Important APIs, Types, And Functions
- `smbsrv_init_signing()` initializes the signing blob, turns signing off, and reads server signing policy via `lpcfg_server_signing_allowed()`.
- `smbsrv_setup_signing()` installs the signing key after authentication using `set_smb_signing_common()` and `smbcli_simple_set_signing()`.
- `smbsrv_signing_check_incoming()` allocates a sequence number and verifies signed incoming packets.
- `smbsrv_sign_packet()` signs outgoing replies or emits the legacy `BSRSPYL ` marker mode.
- `smbsrv_signing_no_reply()` adjusts sequence numbers for commands that consume a request but do not send a reply.

## Control Flow
Every normal SMB1 packet passes through `smbsrv_signing_check_incoming()` in `receive.c`. That assigns `req->seq_num` from `next_seq_num` and increments the connection sequence by two when signing is active. If signing is off, validation succeeds. If signing is on, the function checks the packet is long enough to contain the signature field, validates the MAC using the current key and request sequence, and updates signing-good state. Before normal send, `smbsrv_send_reply()` calls `smbsrv_sign_packet()`, which signs with `req->seq_num + 1`.

## State And Persistence
All persistent signing state lives on `smb_conn->signing`: `mac_key`, engine state, mandatory/allowed flags, and `next_seq_num`. Per-request state is only `seq_num`. Session setup is responsible for moving the connection from off to active signing after authentication.

## Dependencies And Integration Points
Uses raw SMB client signing helpers from `libcli/raw`. Integrated by `receive.c` for validation/no-reply adjustment, `request.c` for outgoing signing, `negprot.c` for advertising signing policy, and `sesssetup.c` for installing the authenticated session key.

## Risks
Sequence numbers are easy to desynchronize around no-reply commands, multi-packet transactions, and secondary transaction requests. `SMB_SIGNING_ENGINE_BSRSPYL` intentionally writes a fixed marker instead of a normal signature. Incoming packets shorter than the security signature field fail when signing is active. Signing setup must be called only after a valid session key exists.

## Test Signals
Cover unsigned connections, mandatory signing negotiation through auth, valid and invalid signed packet MACs, short signed packets, outgoing signature sequence `seq_num + 1`, `SMBntcancel`/no-reply sequence adjustment, and multi-packet transaction secondary sequence handling.
