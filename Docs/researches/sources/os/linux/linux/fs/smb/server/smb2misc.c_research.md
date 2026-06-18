# File Research: sources/os/linux/linux/fs/smb/server/smb2misc.c

This file validates SMB2 request headers, fixed structure sizes, variable data areas, message lengths, and credit charges.

Validation tables:
- `smb2_req_struct_sizes[]` maps SMB2 command indexes to expected request `StructureSize2`.
- `has_smb2_data_area[]` marks commands with variable data buffers.

Header and data-area validation:
- `check_smb2_hdr()` rejects server-to-client SMB2 packets received as requests.
- `smb2_get_data_area_len()` extracts command-specific buffer offset/length for session setup, tree connect, create, query/set info, read, write, query directory, lock, and ioctl.
- It rejects offsets over 4096 and total offset+length beyond `MAX_STREAM_PROT_LEN`.
- `smb2_calc_size()` computes the expected request length from SMB2 header, fixed body, and variable data area. It handles the SMB2 lock structure-size special case.

Credit validation:
- Request length helpers estimate credit needs for query info, set info, read, write, query directory, and ioctl.
- `smb2_validate_credit_charge()` compares client credit charge with calculated requirement, max credits, total granted credits, and outstanding credit limits under `credits_lock`.

Main entry:
- `ksmbd_smb2_check_message()` validates compound-message `NextCommand`, SMB2 header size, command range, fixed structure size, fixed body length, calculated message size, acceptable padding quirks, negotiate special case, and large-MTU credit charge.
- `smb2_negotiate_request()` forwards negotiation to common SMB negotiation handling.

Compatibility notes:
- Allows one-byte implied bcc difference.
- Allows final compound PDU padding to 8-byte alignment.
- Allows small padding differences up to 8 bytes for observed Linux/SMB 3.0.2 clients.
- SMB2 negotiate receives relaxed size handling and is validated deeper in negotiate handling.

Role in this group:
- Called by `server.c` through protocol ops before dispatch.
- Protects SMB2 command handlers and create-context parsing, including `oplock.c`’s `smb2_find_context_vals()`, from malformed packet lengths.
