<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolver.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolver.java

Purpose: Defines the strategy interface for translating an SMB path before or after an SMB response, allowing the client to compose local, symlink, and DFS resolution without hard-wiring it into share operations.

Important APIs/types/functions: LOCAL resolver simply applies the action to the original SmbPath and accepts only StatusHandler.SUCCESS. The reactive resolve variant receives an SMB2Packet response; the proactive variant receives only a path. ResolveAction<T> is the callback invoked with the resolved target.

Control flow: Callers pass an action that performs the real tree connect or create on the resolved target. Decorators decide whether to call the action, delegate to wrapped resolver, or throw PathResolveException.

State and persistence behavior: Interface has no state. LOCAL is a singleton stateless implementation.

Dependencies and integration points: Depends on SMB2Packet, SmbPath, Session, and StatusHandler. Used by Session.connectTree and DiskShare.create/open flows.

Risks: Callback may return null by convention to mean no reroute, so callers must handle null carefully. Resolver chains must expose a compatible statusHandler or initial SMB requests will reject expected symlink/DFS statuses.

Test signals: Verify LOCAL behavior, decorator ordering, null-return handling, and status handler composition for DFS plus symlink chains.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolver.java -->
