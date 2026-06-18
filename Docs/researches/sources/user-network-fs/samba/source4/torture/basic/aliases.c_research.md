# sources/user-network-fs/samba/source4/torture/basic/aliases.c

## Purpose
This torture helper scans SMB1 TRANS2 information levels to discover query/set aliases. It brute-forces many info-level values, records successful responses, compares blobs for identical results, and reports potential alias levels for qfsinfo, qfileinfo, qpathinfo, findfirst, setfileinfo, and setpathinfo.

## Important APIs, Types, And Functions
The suite factory is `torture_trans2_aliases`. Core helpers are `gen_aliases`, `gen_set_aliases`, and test cases `qfsinfo_aliases`, `qfileinfo_aliases`, `qpathinfo_aliases`, `findfirst_aliases`, `setfileinfo_aliases`, and `setpathinfo_aliases`. `struct trans2_blobs` stores a level and output parameter/data blobs for comparison. The file references external `create_complex_file`.

## Control Flow
Query scans initialize an `smb_trans2` request for a specific TRANS2 setup code, create a test file where needed, set the info level field repeatedly, call `smb_raw_trans2`, store successful output blobs, and then compare all success pairs for identical parameter and data blobs. Set scans iterate levels and even data sizes up to 1024 bytes, distinguishing invalid-level errors from size/content errors, and report levels that can reach OK or invalid-parameter responses.

## State And Persistence
The tests create and delete temporary files under the tested share. Alias results live only in talloc lists and torture output. No repository state is changed.

## Dependencies And Integration Points
It depends on raw TRANS2 client APIs, smbcli helpers, dlink lists, blob comparison, and the basic torture suite registration in `base.c`. It exercises server TRANS2 dispatch and info-level compatibility.

## Risks And Test Signals
Risks include long brute-force runtime, server-side side effects from malformed set buffers, reliance on all-zero input buffers, and cleanup after assertion failures. Test signals are the set of accepted levels, aliases with identical output, expected invalid-level behavior, and regressions in TRANS2 compatibility across SMB servers.
