# sources/user-network-fs/impacket/examples/smbclient.py

## Purpose

`smbclient.py` is a command-line wrapper around Impacket's `MiniImpacketShell`. It authenticates to an SMB server and either opens an interactive shell or runs commands from an input file.

## Important APIs, Types, and Functions

`main()` owns all behavior. It parses target/auth/connection/logging options, creates `SMBConnection`, performs NTLM or Kerberos login, instantiates `MiniImpacketShell(smbClient, None, outputfile)`, optionally writes an output-file header, and runs either scripted `onecmd()` calls or `cmdloop()`.

## Control Flow

After parsing, the script normalizes domain and target IP, prompts for a password unless disabled or alternate credentials are present, splits hashes, logs into SMB, and creates the shell. In input-file mode it skips comment lines that start with `#`, prints each command, and sends it to the shell. Without an input file, it enters the interactive command loop.

## State and Persistence Behavior

Remote state depends on commands executed in `MiniImpacketShell` and can include file uploads, deletes, directory changes, and other SMB operations. Locally, `-outputfile` appends a target header and shell actions through the shell implementation. The input file is read but not modified.

## Dependencies and Integration Points

It depends on `SMBConnection`, `MiniImpacketShell`, target parsing, Impacket logger, Kerberos/AES/hash auth, and SMB ports 139/445. It is mainly an entry point for the reusable shell implementation in `impacket.examples.smbclient`.

## Risks and Edge Cases

Input-file processing indexes `line[0]`, so blank lines can raise `IndexError`. Output-file header writing is separate from shell logging and can fail independently. The script does not explicitly log off or close the SMB connection. Command side effects are delegated and can be destructive.

## Test Signals

Mock tests should cover auth option normalization, hash splitting, password prompt suppression, blank/comment/scripted input handling, output-file header creation, and shell invocation. Integration tests should cover interactive login, Kerberos, hash login, and scripted file operations against a test SMB share.
