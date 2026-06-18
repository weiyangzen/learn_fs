<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenTarg.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenTarg.java

Purpose: Encoder/decoder for SPNEGO NegTokenTarg response tokens, including negotiation result, selected mechanism, response token, and MIC.

Important APIs/types/functions: write(Buffer), read(byte[]), parseTagged(), readNegResult(), readSupportedMech(), readResponseToken(), readMechListMIC(), getters/setters for negotiationResult, supportedMech, responseToken, and mechListMic. Overrides writeGss() to emit only the [1] negotiation token without outer SPNEGO OID framing for Samba compatibility.

Control flow: write conditionally adds tagged ASN.1 fields for non-null values, wraps them in a sequence, and writes DER. read parses a DER object and delegates to SpnegoToken.parseSpnegoToken. parseTagged validates expected ASN.1 types for tags 0 through 3 and stores values.

State and persistence behavior: Mutable token fields are stored in memory; byte arrays are stored and returned by reference.

Dependencies and integration points: Uses ASN.1 DER streams/types, Buffer, SpnegoToken, and is part of authentication token exchange.

Risks: Overridden writeGss uses context-specific tag 1 directly and may not match all peers that expect full GSS framing. Byte array setters/getters alias caller/internal arrays. Error message in readNegResult references supportedMech rather than object. No enum abstraction for negotiation result values.

Test signals: Encode/decode all optional fields, absent fields, invalid ASN.1 types per tag, unknown tag, Samba-compatible output form, and mutable array aliasing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenTarg.java -->
