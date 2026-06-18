<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/DFSPathResolver.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/DFSPathResolver.java

Purpose: Decorates another PathResolver with Microsoft DFS namespace resolution for tree connects and file creates. It follows the MS-DFSC step model, uses ReferralCache and DomainCache, and issues FSCTL_DFS_GET_REFERRALS over IPC$ when local or cached path data is insufficient.

Important APIs/types/functions: resolve(Session, SMB2Packet, SmbPath, ResolveAction) reacts to STATUS_PATH_NOT_COVERED and failed root share connects; resolve(Session, SmbPath, ResolveAction) proactively resolves before create; statusHandler() accepts STATUS_PATH_NOT_COVERED in addition to the wrapped resolver. The private step1 through step14 methods encode the DFS state machine. sendDfsReferralRequest(), getReferral(), handleReferralResponse(), handleRootOrLinkReferralResponse(), and handleDCReferralResponse() bridge to SMB2 IOCTL and cache updates. ResolveState carries current DFSPath, action, hostName, and flags; ReferralResult carries status and cache entries.

Control flow: A request starts by converting SmbPath to DFSPath, then checks simple/IPC paths, referral cache, domain cache, root referrals, link referrals, sysvol referrals, and interlinks. A successful cache/referral hit rewrites the matching prefix with the target hint and invokes the caller action with a parsed SmbPath. Target failures can retry hints or throw DFSException for domain/root/link failure.

State and persistence behavior: ReferralCache and DomainCache are in-memory per resolver instance and can persist between operations on the same SMBClient configuration. DFS referral sessions to other hosts may be opened and authenticated with the original AuthenticationContext; IPC$ shares are intentionally not closed to reuse cached shares. No disk persistence is used.

Dependencies and integration points: Depends on com.hierynomus.msdfsc cache/path/message types, SMB2IoctlResponse, Share.ioctlAsync(), Session.connectShare(), Connection.getClient().connect(), and the wrapped resolver, commonly SymlinkPathResolver or PathResolver.LOCAL. DiskShare and Session call this resolver around TREE_CONNECT and CREATE.

Risks: The code is recursive and can loop if referrals form cycles or caches are inconsistent. DFS cross-host authentication opens nested connections that must be cleaned by Session.logoff. getReferral uses a fixed transact timeout; slow DFS servers surface as TransportException wrappers. DOMAIN referral type is declared but unsupported. Retry in step3 uses lookup.getTargetHint() while iterating target, so target-hint advancement deserves tests. Cache TTL and interlink behavior are correctness-critical.

Test signals: Cover unsupported DFS short-circuit, STATUS_PATH_NOT_COVERED create reroute, root referral miss, expired root vs link TTL, SYSVOL/NETLOGON domain path, interlink recursion, IPC$ short-circuit, referral response with no entries, cross-host nested session reuse, and timeout/error conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/DFSPathResolver.java -->
