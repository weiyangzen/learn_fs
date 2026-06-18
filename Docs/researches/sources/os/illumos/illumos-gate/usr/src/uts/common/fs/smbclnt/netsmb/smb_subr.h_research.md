# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_subr.h

## Purpose
Declares shared SMB client utility types, logging macros, timeout tunables, credential helpers, string/time/error conversion helpers, signing/encryption APIs, and SMB1/SMB2/SMB3 protocol operation entry points.

## Key Elements
Provides logging macros (`SMBERROR`, `SMBPANIC`, `SMBSDEBUG`, `SMBIODEBUG`, `NBDEBUG`) built on `smb_errmsg`, debug-entry handling, Unicode type aliases, and `smbfattr_t`, the native-endian file attribute bundle used by create/query paths.

Declares global timeout tunables for SMB1 and SMB2 operations, transport device globals, credential lifecycle helpers, DOS/NT status mapping helpers, SMB string encode/decode routines, socket-address helpers, SMB1 and SMB2 signing initialization/sign/verify helpers, MAC-key derivation helpers, SMB3 crypto mechanism/key/message helpers, SMB1 protocol operations, SMB2 protocol operations, SMB2 IOCTL/read/write/create/close operations, SMB3 preauth and negotiate-context helpers, and SMB time conversion routines.

## Dependencies
Includes kernel cmn_err/lock/note headers, `mchain.h`, and `smb_conn.h`. It acts as the common include surface for many `netsmb` C files.

## Behavior/Risks
This header is the cross-module contract for the SMB client protocol stack. Prototype or type changes ripple through SMB1, SMB2, SMB3 crypto, request, user ioctl, and smbfs mount code. Timeout variables are externally tunable and affect I/O behavior. The declared signing/encryption helpers encode security-critical sequencing and must remain paired with the IOD send/receive paths.
