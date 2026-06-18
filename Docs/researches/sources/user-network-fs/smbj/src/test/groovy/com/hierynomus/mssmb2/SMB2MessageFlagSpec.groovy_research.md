# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2MessageFlagSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2MessageFlagSpec.groovy

Purpose: validates conversion from raw SMB2 flag bitmask to `EnumSet<SMB2MessageFlag>`. Control flow passes `0x10000001` through `EnumWithValue.EnumUtils.toEnumSet` and asserts exactly `SMB2_FLAGS_DFS_OPERATIONS` and `SMB2_FLAGS_SERVER_TO_REDIR`.

State and persistence: none. Dependencies are `SMB2MessageFlag` and shared enum-with-value utilities. Integration point is header flag parsing and serialization. Risk covered is high-bit flag handling in a `long` bitmask and avoiding accidental extra flags. Test signal is focused and small; it does not cover reverse serialization or unknown bits.
