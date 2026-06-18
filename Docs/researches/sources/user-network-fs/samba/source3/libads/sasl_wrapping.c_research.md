# sources/user-network-fs/samba/source3/libads/sasl_wrapping.c

## Purpose

`sasl_wrapping.c` installs an OpenLDAP sockbuf transport layer that frames, signs, seals, unwraps, and streams LDAP bytes after SASL negotiation.

## Important APIs, Types, and Functions

`ndr_print_ads_saslwrap_struct` prints wrapper state for diagnostics. `ads_setup_sasl_wrapping` installs the `Sockbuf_IO` layer and records mechanism-specific `ads_saslwrap_ops`. Internal helpers manage setup/remove, input buffer prepare/grow/shrink, output buffer prepare/shrink, `ads_saslwrap_read`, `ads_saslwrap_write`, `ads_saslwrap_ctrl`, and close.

## Control Flow

Reads first collect a four-byte big-endian wrapped length, validate it against min/max wrapped bounds, grow the buffer, read the complete wrapped payload, call the configured `unwrap` hook once, then satisfy caller reads from the unwrapped bytes. Writes split input to `out.max_unwrapped`, allocate room for length plus signature/payload, call the configured `wrap` hook, write the length header, then drain the wrapped buffer to the next sockbuf layer.

## State and Persistence Behavior

All state is inside `struct ads_saslwrap`: current sockbuf descriptor, talloc memory context, wrap type, ops/private data, input offset/needed/left/bounds/buffer, and output offset/left/bounds/buffer. It is live for the LDAP connection lifetime and freed through `ads_disconnect`.

## Dependencies and Integration Points

It depends on OpenLDAP `Sockbuf_IO`, Samba ADS wrapper structures, `ads_saslwrap_ops` provided by `sasl.c`, and NDR printing utilities. It integrates directly into OpenLDAP's socket stack after a successful sign/seal SASL bind.

## Risks and Test Signals

Risks include partial-read/write `EAGAIN` semantics, corrupted length headers, min-wrapped truncation assumptions, buffer lifetime leaks on wrap/unwrap failure, and incorrect `DATA_READY` behavior when unwrapped bytes remain. Tests should drive partial header/payload reads, oversized and undersized wrapped frames, fragmented writes, sign-only and seal wrapping, unwrap failures mapping to `EACCES`, and disconnect cleanup.
