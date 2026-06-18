<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/ObjectIdentifiers.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/ObjectIdentifiers.java

Purpose: Central holder for the SPNEGO object identifier constant.

Important APIs/types/functions: public static final ASN1ObjectIdentifier SPNEGO with value 1.3.6.1.5.5.2.

Control flow: SpnegoToken.writeGss inserts this OID into the GSS application sequence, and NegTokenInit.read uses it in validation messages.

State and persistence behavior: Immutable constant only.

Dependencies and integration points: Depends on ASN1ObjectIdentifier and is imported by SPNEGO token classes.

Risks: Class is not final and has implicit public constructor, though it only contains constants. Equality validation is left to callers.

Test signals: Constant value, identity use in encoded NegTokenInit, and no accidental mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/ObjectIdentifiers.java -->
