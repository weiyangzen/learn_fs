# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/pdu.h

## Purpose
Private SMBDirect wire-format definitions for negotiation and data-transfer PDUs.

## Constants
- `SMBDIRECT_V1` is `0x0100`.
- Minimums from MS-SMBD:
  - `SMBDIRECT_MIN_RECEIVE_SIZE` = 128
  - `SMBDIRECT_MIN_FRAGMENTED_SIZE` = 131072
- Data PDU layout constants:
  - `SMBDIRECT_DATA_MIN_HDR_SIZE`
  - `SMBDIRECT_DATA_OFFSET`
- `SMBDIRECT_FLAG_RESPONSE_REQUESTED` requests an immediate response/keepalive.

## Wire Structures
- `struct smbdirect_negotiate_req`
  - min/max version
  - credits requested
  - preferred send size
  - max receive size
  - max fragmented size
- `struct smbdirect_negotiate_resp`
  - min/max/negotiated version
  - credits requested/granted
  - NT status
  - max read/write size
  - preferred send size
  - max receive size
  - max fragmented size
- `struct smbdirect_data_transfer`
  - credits requested/granted
  - flags
  - remaining data length
  - data offset and length
  - padding
  - flexible payload buffer

## Notes
- All PDU structures are packed and use little-endian fields.
- These structures are consumed by `accept.c`, `connect.c`, and `connection.c`.
