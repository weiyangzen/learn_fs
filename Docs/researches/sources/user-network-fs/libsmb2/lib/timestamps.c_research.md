<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/timestamps.c -->
# sources/user-network-fs/libsmb2/lib/timestamps.c

Purpose: Converts timestamps between libsmb2 timeval form and Windows FILETIME units used by SMB2 metadata.

Important APIs, types, and functions: Exports `smb2_timeval_to_win` and `smb2_win_to_timeval`.

Control flow: Conversion is direct arithmetic: Unix seconds are scaled by 10,000,000, microseconds by 10, and the Windows epoch offset `116444736000000000` is added or subtracted.

State and persistence behavior: Stateless pure conversion functions. No allocation or persistence.

Dependencies and integration points: Depends on `struct smb2_timeval` from libsmb2 public/private headers. Used by metadata encoding and decoding paths.

Risks: No range checks are performed. Values before the Windows epoch or extreme future values can underflow/overflow unsigned arithmetic when represented as `uint64_t`.

Test signals: No direct test in this subset; metadata tests and directory/stat paths provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/timestamps.c -->
