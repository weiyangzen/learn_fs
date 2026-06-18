# sources/user-network-fs/impacket/examples/Get-GPPPassword.py

## Purpose

`Get-GPPPassword.py` finds Group Policy Preferences XML files containing `cpassword`, decrypts the known AES-CBC protected value, and prints recovered credentials. It can scan a remote SMB share such as SYSVOL or parse a local XML file.

## Important APIs, Types, and Functions

`GetGPPasswords` owns an `SMBConnection` and share name. `list_shares` prints available shares. `find_cpasswords` breadth-first scans directories for XML files. `parse` retrieves a remote file into `io.BytesIO`, detects encoding with `charset_normalizer`, and calls `parse_xmlfile_content` if `cpassword` is present. `parse_xmlfile_content` parses XML DOMs and extracts known GPP property fields. `decrypt_password` base64-decodes and decrypts with the published GPP AES key and zero IV. Helper functions `parse_args`, `parse_target`, and `init_smb_session` handle CLI, credentials, and SMB login.

## Control Flow

In `LOCAL` mode, the script opens the provided `-xmlfile`, parses it, and displays results. In remote mode, it parses the target, prompts for a password when needed, initializes SMB or Kerberos login, prints shares, and scans `-base-dir` on the selected share. Each matching XML file is fetched by stream, decoded, searched for `cpassword`, parsed according to root XML type (`ScheduledTasks`, `Groups`, or default), decrypted, and displayed.

## State and Persistence Behavior

The script reads remote SMB files and local XML files but does not modify them. It stores scan queues, result dictionaries, and in-memory file buffers. It prints decrypted passwords to logs/stdout, which is the main side effect. No output file option is present.

## Dependencies and Integration Points

It depends on Impacket SMB connection classes, Impacket example target parsing, PyCryptodome AES/padding, `charset_normalizer`, Python DOM XML parsing, and SMB dialect constants. It integrates with Windows SYSVOL/GPP XML layout and SMB ports 139/445.

## Risks and Edge Cases

The XML parsing uses `minidom.parseString`; while local/remote SYSVOL XML is expected, malformed or hostile XML can still cause parser exceptions or resource use. Decrypted credentials are intentionally exposed in logs. The BFS ignores access-denied folders after debug logging. Some file handles are closed only on certain branches; `BytesIO` cleanup is not critical but inconsistent. Base64 padding repair handles common cases but malformed `cpassword` can raise. Local mode opens files without context managers.

## Test Signals

Unit tests can cover `decrypt_password` with known GPP samples, padding variants, empty values, and `parse_xmlfile_content` for Groups and ScheduledTasks XML. Integration tests should mock SMB `listPath`/`getFile` traversal, access-denied directories, encoding detection, and remote Kerberos/NTLM login selection.
