# sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_collections.swift

Purpose: Holds disabled experimental Swift C++ interop conformances for FoundationDB map iterator types. It is currently a placeholder for future toolchain support.

Important APIs/types/functions: Under `#if NOTNEEDED`, it would conform `Map_UID_CommitProxyVersionReplies.const_iterator` and `MAP_UInt64_GetCommitVersionReply.const_iterator` to `UnsafeCxxInputIterator`, and their map types to `CxxSequence`, with equality operators.

Control flow: No active runtime control flow because the whole implementation is compile-time disabled.

State and persistence behavior: None. If enabled, it would only affect iteration semantics for imported C++ containers.

Dependencies and integration points: Imports `Flow`, `FDBServer`, and `Cxx`. The comments tie it to Swift toolchain limitations around C++ map interop.

Risks: Equality implementations currently return `true`, which would be incorrect if enabled as-is and could break sequence iteration. Any future activation must replace placeholders with real iterator comparison.

Test signals: No active tests. Build coverage confirms the disabled block stays excluded; future enabling would require Swift iteration tests over the bridged map types.
