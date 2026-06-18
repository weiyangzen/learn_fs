<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SMB2GuestSigningRequiredException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SMB2GuestSigningRequiredException.java

Purpose: Domain-specific runtime exception thrown when configuration requires SMB message signing but authentication yielded a guest account, which cannot satisfy that requirement.

Important APIs/types/functions: No extra API beyond the default constructor message.

Control flow: Authentication/session setup code can throw it after session flags identify guest access while signing is required.

State and persistence behavior: Stateless exception.

Dependencies and integration points: Extends SMBRuntimeException and relates to SessionContext.isGuest()/isSigningRequired().

Risks: Only meaningful if raised at the exact point guest state is known; otherwise later send() failures may be less explanatory.

Test signals: Verify message, type, and authentication path behavior for guest plus required signing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SMB2GuestSigningRequiredException.java -->
