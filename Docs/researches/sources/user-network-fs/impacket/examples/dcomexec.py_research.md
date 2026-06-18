# sources/user-network-fs/impacket/examples/dcomexec.py

## Purpose
`dcomexec.py` provides semi-interactive or one-shot remote command execution through DCOM automation objects: `ShellWindows`, `ShellBrowserWindow`, and `MMC20.Application`. It resembles PsExec-style execution but uses COM method invocation and optionally SMB only for command output and file transfer.

## Important APIs, Types, and Functions
`DCOMEXEC` owns authentication, DCOM object selection, SMB output setup, and shell creation. `getInterface()` parses returned `OBJREF` variants and builds an `IRemUnknown2` interface. `run()` logs into SMB when output is enabled, connects via `DCOMConnection`, instantiates the requested COM object, obtains the dispatch method (`ShellExecute` or `ExecuteShellCommand`), and starts `RemoteShell` or `RemoteShellMMC20`.

`RemoteShell` extends `cmd.Cmd` and implements local shell commands (`lcd`, `lput`, `lget`, `!`), remote directory tracking, output retrieval through SMB, command encoding, and dispatch invocation. `RemoteShellMMC20` overrides `execute_remote()` for the MMC method signature. `load_smbclient_auth_file()` reads `username`, `password`, and `domain` values from smbclient-style auth files. The CLI supports hashes, Kerberos, keytab, COM version override, codec, shell type, output suppression, and silent command mode.

## Control Flow
Main parses options, resolves credentials, optionally loads an auth file or keytab, prompts for a password, and instantiates `DCOMEXEC`. `run()` creates an SMB connection unless output is disabled or the command is silent, then creates a DCOM connection with `oxidResolver=True`. Depending on `-object`, it walks different `IDispatch` property/method paths to reach an application view. If a command was supplied, it runs one command and exits; otherwise it enters the interactive command loop.

Remote execution builds COM `DISPPARAMS` and `VARIANT` arguments. Normal commands run under `cmd.exe /Q /c`, PowerShell commands are UTF-16LE base64 encoded, and output is redirected to `\\127.0.0.1\<share>\<OUTPUT_FILENAME>`. The SMB client polls until sharing violations stop, reads output, and deletes the remote output file.

## State and Persistence
Local state includes current remote directory, prompt, output buffer, selected shell, and SMB/DCOM handles. Remote transient state includes a short-lived output file under the chosen administrative share and any side effects of executed commands. `lput` and `lget` explicitly write or read remote/local files. DCOM object instances are quit through `do_exit()`.

## Dependencies and Integration Points
The script integrates with Impacket DCOM/OAUT structures, SMBConnection, Kerberos keytab support, and Windows COM automation. It requires network access to DCOM/RPC endpoints and, for output or transfer, SMB administrative shares.

## Risks
This is remote code execution tooling; all inputs to the remote shell have target-side side effects. Output filenames are based on a truncated timestamp and may collide. Command output is written to an administrative share and may remain if cleanup fails. `silentcommand` suppresses normal shell behavior and output. Broad exception handling exits the process, and Kerberos is noted as problematic in a file TODO. Codec mismatch can corrupt displayed output.

## Test Signals
Tests should cover auth-file parsing errors, command construction for cmd and PowerShell, SMB output polling/deletion, local file transfer path normalization, unsupported object handling, COM version parsing, and nooutput/silentcommand validation. Integration tests require Windows targets with each COM object available, SMBv1/2/3 dialects, Kerberos/NTLM auth, and denied DCOM/SMB cases.
