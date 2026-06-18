# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_signing.c

Implements SMB1 message signing for the SMB server. The file calculates and verifies 8-byte SMB1 MAC signatures over mbuf chains using MD5 via the helper layer in `smb_sign_kcf.c`.

`smb_sign_begin` initializes signing after session setup. It ignores anonymous/guest-like paths without a session key, serializes setup under the session lock, initializes the MD5 mechanism once per session, builds the MAC key from the user session key plus the NTLM response for non-extended-security logons, initializes sequence numbers, and enables signing/checking flags according to negotiated server security mode.

`smb_sign_calc` is the central signature function. It computes `head(MD5(MACKey || SMBMsg), 8)` after copying the SMB header into an aligned temporary union, replacing the signature field with the little-endian sequence number and zero padding, then digesting the remainder of the mbuf chain from after the SMB header. It returns failure if signing material is absent or KCF operations fail.

`smb_sign_check_request` verifies normal SMB1 requests using `sr->sr_seqnum`, skipping secondary transaction commands because they share the original transaction sequence. In debug builds, `smb_sign_find_seqnum` can search nearby sequence numbers and correct the session sequence for diagnostics. `smb_sign_check_secondary` verifies secondary transactions using `reply_seqnum - 1` and records the reply sequence number. `smb_sign_reply` computes and writes the response signature at offset 14.

`smb_sign_fini` frees the per-session signing mechanism during session teardown. Key state lives in `session->signing`, and the code assumes SMB1 fixed header layout constants: 32-byte header, signature offset 14, signature size 8.
