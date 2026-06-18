# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/ConnectionContext.java

Purpose: `ConnectionContext` stores negotiated connection metadata and capability decisions.

Important APIs and control flow: constructed with client GUID, server address, and client config. `negotiated` installs the negotiated response, server object, `NegotiatedProtocol`, cipher, compression algorithms, preauth hash data, and server time offset. Capability helpers report signing, encryption, DFS, leasing, multichannel, and multicredit support.

State, dependencies, and integration: it references a `Server`, client capabilities, negotiated protocol, SMB 3.1.1 preauth fields, cipher, compression ids, Windows version, and NetBIOS name. It feeds session setup, encryption, signing, and path resolution.

Risks: `supportsMultiCredit()` consults server capabilities before `negotiatedProtocol` is initialized, which is intentional during negotiation but fragile. GSS negotiate token remains empty in this code. Tests should verify capability derivation for SMB2, SMB3, and SMB3.1.1, time offset, preauth defaults, and encryption preference logic.
