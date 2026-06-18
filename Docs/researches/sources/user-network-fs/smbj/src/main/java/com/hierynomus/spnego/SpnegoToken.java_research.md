<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoToken.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoToken.java

Purpose: Abstract base for SPNEGO token classes, providing common GSS-API wrapper writing and CHOICE/SEQUENCE parsing.

Important APIs/types/functions: Constructor takes tokenTagNo and tokenName. writeGss(Buffer, ASN1Object) emits [APPLICATION 0] sequence of SPNEGO OID plus context-specific negotiation token. parseSpnegoToken(ASN1Object) validates expected CHOICE tag and inner sequence, then dispatches each tagged field to parseTagged(). Abstract write() and parseTagged().

Control flow: Subclasses build or parse token-specific fields; this base handles outer SPNEGO/GSS structure and shared validation. NegTokenTarg overrides writeGss for a special output form but still uses parseSpnegoToken.

State and persistence behavior: Holds token tag number and human-readable token name. No persistence.

Dependencies and integration points: Depends on ASN.1 DER output types, ObjectIdentifiers.SPNEGO, Buffer, and subclass implementations.

Risks: tokenName can be null for RawToken, producing weak error messages if parsing were invoked. parseSpnegoToken demands all sequence elements are tagged objects and rejects extensions not modeled by subclasses. writeGss uses explicit/implicit constructor flags that must match ASN.1 library semantics.

Test signals: Outer GSS encoding, CHOICE tag validation, non-sequence rejection, non-tagged child rejection, subclass dispatch order, and NegTokenTarg override compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoToken.java -->
