<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit2.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit2.java

Purpose: Microsoft NegTokenInit2 parser extension that understands tag layout with negHints before mechListMIC.

Important APIs/types/functions: Overrides parseTagged(ASN1TaggedObject) from NegTokenInit. Tags 0 mechTypes, 1 reqFlags ignored, 2 mechToken, 3 negHints ignored, and 4 mechListMIC ignored.

Control flow: The inherited read path invokes this parseTagged so Init2 tokens can be accepted without treating negHints tag 3 as MIC. ADS_IGNORE_PRINCIPAL strings are ignored.

State and persistence behavior: Inherits mechTypes and mechToken state from NegTokenInit; no new fields are stored.

Dependencies and integration points: Used wherever an SPNEGO initiator token may include Microsoft negHints. Depends on ASN1TaggedObject and NegTokenInit parsing helpers.

Risks: negHints and MIC are ignored entirely, so callers cannot use server hints or MIC validation. It inherits write behavior from NegTokenInit, so it does not emit Init2-specific negHints.

Test signals: Parse Init2 with negHints tag 3, parse MIC tag 4, inherited mech list/token parsing, unknown tag failure, and ADS ignore behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit2.java -->
