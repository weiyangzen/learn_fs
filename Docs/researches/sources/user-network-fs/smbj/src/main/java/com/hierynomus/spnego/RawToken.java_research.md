<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/RawToken.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/RawToken.java

Purpose: SpnegoToken implementation that writes prebuilt raw token bytes without parsing or ASN.1 reconstruction.

Important APIs/types/functions: Constructor RawToken(byte[]), write(Buffer), and parseTagged() which throws UnsupportedOperationException.

Control flow: write copies rawToken into the output buffer if non-null. No validation, framing, or decoding is performed.

State and persistence behavior: Stores caller-provided byte array by reference. Stateless after write except for the array.

Dependencies and integration points: Useful when an authentication mechanism already produced a complete token. Extends SpnegoToken only to share write contract.

Risks: Caller can mutate rawToken after construction. Null token silently writes nothing. parseTagged throws unchecked UnsupportedOperationException rather than SpnegoException.

Test signals: Raw bytes emitted unchanged, null token no-op, mutation aliasing, and parseTagged unsupported behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/RawToken.java -->
