# sources/user-network-fs/samba/source3/smbd/smb1_signing.c

### Purpose
`smb1_signing.c` adapts Samba's generic SMB1 signing engine to the `smbXsrv_connection` server connection. It validates incoming signatures, signs outgoing packets, initializes signing state according to server policy, supports shared-memory signing state for async echo handling, records negotiated signing flags, and activates signing after session setup provides keys.

### Important APIs, Types, And Functions
- `smb1_srv_check_sign_mac()` validates an incoming SMB1 PDU and returns the sequence number. It has a trusted-channel shortcut that reads sequence/status fields directly from the security signature field.
- `smb1_srv_calculate_sign_mac()` signs outgoing SMB1 PDUs for a supplied sequence number.
- `smb1_srv_cancel_sign_response()` cancels a one-way reply in the signing sequence.
- `struct smbd_shm_signing`, `smbd_shm_signing_alloc()`, `smbd_shm_signing_free()`, and `smbd_shm_signing_destructor()` provide a tiny two-allocation shared-memory allocator used when the async SMB echo handler needs signing state visible across processes/contexts.
- `smb1_srv_init_signing()` creates `conn->smb1.signing_state` with allowed/desired/mandatory policy from loadparm and optional shared memory allocation.
- `smb1_srv_set_signing_negotiated()`, `smb1_srv_is_signing_active()`, `smb1_srv_is_signing_negotiated()`, and `smb1_srv_set_signing()` expose negotiation, state checks, and activation.

### Control Flow
Incoming signing checks ignore non-session NetBIOS messages. Normal packets compute the next expected sequence with `smb1_signing_next_seqnum()` and validate via `smb1_signing_check_pdu()`. Trusted-channel packets must be long enough, must carry an OK status in the signature field, and pass through the embedded sequence number.

Outgoing signing similarly ignores non-session messages, strips the NBT header for signing, and delegates to `smb1_signing_sign_pdu()`. Initialization asks loadparm whether server signing is allowed and mandatory; if async echo handling is enabled it allocates 4096 bytes of anonymous shared memory and initializes the generic signing engine with custom alloc/free callbacks. Activation requires a non-empty user session key and either negotiated or mandatory signing, then calls `smb1_signing_activate()`.

### State And Persistence Behavior
The main state is `conn->smb1.signing_state`. In async echo mode, a `struct smbd_shm_signing` talloc child owns anonymous shared memory and tracks up to two allocation regions used by the signing engine. No persistent disk state is written. Sequence numbers and active/negotiated/mandatory flags live in the signing engine.

### Dependencies And Integration Points
This file depends on `../libcli/smb/smb_signing.h`, loadparm server-signing policy, `lp_async_smb_echo_handler()`, anonymous shared memory helpers, and SMB packet length/header macros. It is used by session setup to negotiate/activate signing and by the SMB1 receive/send paths to check and calculate MACs. `smb1_reply.c` also queries active signing to disable raw I/O and sendfile paths.

### Risks
- Sequence-number handling is integrity-critical; incorrect cancellation or trusted-channel parsing can desynchronize signing or accept forged packets.
- Shared-memory allocation assumes the signing engine only allocates two chunks. If the engine allocation pattern changes, the custom allocator can fail unexpectedly.
- Non-session-message bypass relies on correct NetBIOS message type interpretation.
- Activation deliberately returns without error when signing was not negotiated and not mandatory; callers must enforce mandatory policy elsewhere.

### Test Signals
Tests should cover signing initialization under allowed/disabled/mandatory policy, activation after valid session keys, mandatory client/server combinations, bad signature rejection, sequence cancellation for one-way requests, raw I/O/sendfile disabled when active, trusted-channel validation with short packets and non-OK embedded statuses, and async echo-handler shared-memory initialization/failure paths.
