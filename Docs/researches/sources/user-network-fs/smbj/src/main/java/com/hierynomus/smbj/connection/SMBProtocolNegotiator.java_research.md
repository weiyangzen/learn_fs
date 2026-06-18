# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBProtocolNegotiator.java

Purpose: `SMBProtocolNegotiator` sends SMB negotiate requests, validates responses, and populates connection negotiation context.

Important APIs and control flow: `negotiateDialect` chooses SMB2-only or multiprotocol negotiation, checks NT status, parses SMB3.1.1 negotiate contexts, validates server identity against `ServerList`, and updates `ConnectionContext`. SMB3.1.1 handling enforces single preauth and encryption contexts, accepts compression capabilities, and computes the preauth hash from zero state plus request and response bytes. Multiprotocol negotiation sends SMB1 negotiate first and falls back to SMB2-only on SMB_2XX.

State, dependencies, and integration: it owns a temporary `NegotiationContext` containing request, response, cipher, compression ids, preauth hash, and server. It uses security digest providers, packet bytes, server cache, and connection send/future paths.

Risks: unknown SMB3.1.1 contexts throw rather than ignoring future extensions. Compression is recorded but not fully implemented. Tests should cover SMB2-only, multiprotocol fallback, unsuccessful status, duplicate negotiate contexts, preauth hash vectors, server cache mismatch, and encryption cipher selection.
