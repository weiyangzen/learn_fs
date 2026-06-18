# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/common/SmbPathSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/common/SmbPathSpec.groovy

Purpose: Spock tests for SMBJ common UNC path parsing and manipulation. It covers `SmbPath.parse`, constructor behavior, equality/hashCode, UNC rendering, host/share comparison, slash normalization, child path construction, and parent calculation.

State and persistence: immutable path values only. Dependencies are the common `SmbPath` model and Spock tables. Integration point is client/session/share routing and DFS path resolution. Risks covered include mixed slash styles, case/host/share equality semantics, missing path components, and parent calculations at root/share boundaries. Test signal is broad for the older SMBJ path model but separate from the NIO `smbfs.SmbPath` tests.
