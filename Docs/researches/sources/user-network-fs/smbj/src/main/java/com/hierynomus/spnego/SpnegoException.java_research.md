<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoException.java

Purpose: Checked exception for SPNEGO encode/decode failures.

Important APIs/types/functions: Constructors for message and message plus IOException cause.

Control flow: SPNEGO token read/write methods wrap IOException and structural ASN.1 mismatches in SpnegoException so authentication code can distinguish token errors.

State and persistence behavior: Exception state only.

Dependencies and integration points: Used by NegTokenInit, NegTokenInit2, NegTokenTarg, RawToken, and SpnegoToken.

Risks: Only IOException cause constructor exists; non-IO causes must be wrapped differently or lost. No status/code field for protocol error category.

Test signals: Message preservation, cause preservation, and propagation from invalid DER/token shapes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoException.java -->
