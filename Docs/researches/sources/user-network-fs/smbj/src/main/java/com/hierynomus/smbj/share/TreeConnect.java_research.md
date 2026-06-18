<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/TreeConnect.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/TreeConnect.java

Purpose: Represents an SMB tree connect and owns tree disconnect plus share capabilities and negotiated tree-level metadata.

Important APIs/types/functions: close(), getShareName(), getTreeId(), getSession(), getMaximalAccess(), isDfsShare(), isCAShare(), isScaleoutShare(), getConfig(), getNegotiatedProtocol(), and toString().

Control flow: close sends SMB2_TREE_DISCONNECT via Session.send, waits for transact timeout, throws SMBApiException on non-success, and publishes TreeDisconnected in finally so Session can remove cache entries.

State and persistence behavior: Holds treeId, SmbPath, Session, capabilities, negotiated protocol, config, event bus, maximalAccess, and encryptData flag derived from share flags and encryption support. No persistence.

Dependencies and integration points: Created by Session.connectTree and embedded in Share. Uses SMBEventBus and TreeDisconnected events.

Risks: encryptData is computed but not exposed or used in this file; actual per-share encryption may be incomplete elsewhere. bus is assumed non-null. Publishing disconnect in finally happens even if disconnect send fails.

Test signals: Tree disconnect success/failure, event publication on failure, capability predicates, maximal access exposure, share flag encryption calculation expectations, and toString shape.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/TreeConnect.java -->
