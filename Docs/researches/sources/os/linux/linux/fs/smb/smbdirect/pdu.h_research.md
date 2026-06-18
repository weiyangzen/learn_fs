# File Research: sources/os/linux/linux/fs/smb/smbdirect/pdu.h

Defines local SMB Direct protocol constants and packed wire-format PDUs used by the SMB Direct implementation.

Contents:
- `SMBDIRECT_V1` protocol version constant.
- Minimum receive and fragmented sizes from MS-SMBD:
  - `SMBDIRECT_MIN_RECEIVE_SIZE`
  - `SMBDIRECT_MIN_FRAGMENTED_SIZE`
- Packed negotiate request:
  - `struct smbdirect_negotiate_req`
  - fields for min/max version, credits requested, preferred send size, max receive size, and max fragmented size.
- Packed negotiate response:
  - `struct smbdirect_negotiate_resp`
  - fields for version range, negotiated version, credits requested/granted, NT status, max read/write size, preferred send size, max receive size, and max fragmented size.
- Data-transfer constants:
  - `SMBDIRECT_DATA_MIN_HDR_SIZE`
  - `SMBDIRECT_DATA_OFFSET`
  - `SMBDIRECT_FLAG_RESPONSE_REQUESTED`
- Packed data-transfer PDU:
  - `struct smbdirect_data_transfer`
  - fields for credits, flags, remaining data length, data offset, data length, padding, and variable payload.

Usage:
- `accept.c` and `connect.c` use negotiate PDUs.
- `connection.c` uses data-transfer PDUs for send/receive, fragmentation, credit grants, and keepalive response requests.

Maintenance notes:
- All multibyte fields are little-endian wire fields and are converted at use sites.
- Structs are `__packed`; any protocol extension should preserve explicit endian types and avoid implicit padding.
