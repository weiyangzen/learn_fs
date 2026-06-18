<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit.java

Purpose: Encoder/decoder for SPNEGO NegTokenInit tokens with GSS-API application framing and mechanism list/token fields.

Important APIs/types/functions: write(Buffer), read(byte[]), parseTagged(), readMechToken(), readMechTypeList(), addSupportedMech(), setMechToken(), getSupportedMechTypes(). Constants include ADS_IGNORE_PRINCIPAL.

Control flow: write builds a NegTokenInit sequence with optional mechTypes and mechToken, then SpnegoToken.writeGss wraps it with SPNEGO OID and [APPLICATION 0]. read parses DER from a little-endian Buffer stream, validates application class and SPNEGO OID object type, then delegates to parseSpnegoToken. parseTagged accepts tags 0 mechTypes, 1 reqFlags ignored, 2 mechToken, 3 mechListMIC ignored, and ignores ADS compatibility hints.

State and persistence behavior: Stores mutable mechTypes list and mechToken byte array in memory.

Dependencies and integration points: Uses hierynomus ASN.1 DER encoder/decoder, ASN1Sequence/TaggedObject/ObjectIdentifier/OctetString, Buffer, ObjectIdentifiers.SPNEGO, and SpnegoToken.

Risks: read validates OID type but not equality to SPNEGO. getSupportedMechTypes returns mutable internal list. setMechToken stores caller array by reference. reqFlags and MIC are ignored.

Test signals: Write/read roundtrip with multiple mechs and token, invalid application tag, non-OID first sequence element, unknown tagged field, ADS ignore principal input, mutable getter/setter aliasing, and empty optional fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit.java -->
