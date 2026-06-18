# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/NegotiatedProtocol.java

Purpose: `NegotiatedProtocol` is an immutable summary of the chosen SMB dialect and negotiated IO limits.

Important APIs and control flow: constructor stores dialect and max transact/read/write sizes. If multi-credit is not supported, sizes are clamped with `Math.max(..., SINGLE_CREDIT_PAYLOAD_SIZE)`.

State, dependencies, and integration: `ConnectionContext` exposes it to sessions, shares, and send-size calculations.

Risks: the clamping direction should be reviewed against protocol intent; single-credit connections usually need an upper bound, not a larger minimum. Tests should cover size behavior with and without multicredit and dialect propagation.
