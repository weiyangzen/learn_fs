<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SessionContext.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SessionContext.java

Purpose: Holds negotiated per-session security state, session flags, and SMB3 derived keys.

Important APIs/types/functions: established(SMB2SessionSetup) stores session flags. isSigningRequired(), isEncryptData(), setters, isAnonymous(), isGuest(), session/signing/decryption/encryption/application key getters and setters, and preauth hash copy setter/getter.

Control flow: Authentication populates flags and keys, then Session.send(), Session.shouldEncryptData(), and higher-level code query the context for signing/encryption decisions and identity flags.

State and persistence behavior: In-memory security state only. setPreauthIntegrityHashValue copies the input array, but getPreauthIntegrityHashValue returns the internal array directly.

Dependencies and integration points: Depends on SMB2SessionSetup flags and javax.crypto SecretKey/SecretKeySpec. Integrated with Session, Signatory, PacketEncryptor, and SMB 3.1.1 preauth hashing.

Risks: isAnonymous()/isGuest() will throw if established() has not initialized sessionFlags. Preauth hash getter leaks mutable internal state. Key setters accept nullable values and later send paths must enforce requirements.

Test signals: Established guest/null flags, signing/encryption toggles, key propagation, preauth defensive-copy input behavior, and unestablished access behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SessionContext.java -->
