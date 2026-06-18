# sources/user-network-fs/impacket/examples/psexec.py

## Purpose

`psexec.py` implements PsExec-like remote command execution using the bundled RemCom service. It authenticates over SMB/RPC, installs a service binary, sends a command over named pipes, and provides an interactive remote shell with upload/download helpers.

## Important APIs, Types, and Functions

`RemComMessage` and `RemComResponse` model the named-pipe protocol structures. `PSEXEC` manages credentials, command, service options, optional executable/file copy, and RPC transport. `PSEXEC.run()` creates an `ncacn_np` binding to `\pipe\svcctl`; `doStuff()` connects, installs `remcomsvc.RemComSvc()` or a user-supplied binary through `serviceinstall.ServiceInstall`, opens `\RemCom_communicaton`, writes the command packet, starts three pipe threads, waits for the response, uninstalls, and cleans copied files.

`Pipes` opens separate SMB connections for each named pipe. `RemoteStdOutPipe` and `RemoteStdErrPipe` read remote output, buffer by prompt/newline, decode with `CODEC`, and suppress echoed commands via global `LastDataSent`. `RemoteStdInPipe` starts `RemoteShell`, whose commands include local shell execution, `lcd`, `lget`, `lput`, and default remote command submission.

## Control Flow

Main parses target, command, copy and binary options, authentication material, keytab, SMB port, service name, and remote binary name. It sets the output codec, parses target credentials, loads keytab keys when requested, prompts for missing password, defaults to `cmd.exe`, constructs `PSEXEC`, and calls `run()`. The remote process lifetime determines when `doStuff()` exits with the RemCom error code.

## State and Persistence Behavior

The script writes significant remote state: a temporary service and executable on an administrative share, optionally a copied file for execution, and named-pipe traffic. It attempts to uninstall the service and delete copied files on both success and error. Locally, `lget` downloads files into the current directory, `lput` reads local files, and keytab loading mutates options for Kerberos.

## Dependencies and Integration Points

Dependencies include SMB, DCE/RPC `svcctl`, Impacket `remcomsvc`, `serviceinstall`, `SMBConnection`, Kerberos keytab support, and Windows administrative shares. It requires service-control-manager access and file write privileges on the target. It integrates with both NTLM and Kerberos flows, preserving SMB dialect for pipe connections.

## Risks and Edge Cases

The tool is high impact: it creates services and executes commands remotely. Cleanup depends on reaching exception handlers and may fail if the process is interrupted or the target disconnects. Global variables `dialect` and `LastDataSent` coordinate threads and can race. Several broad `except` blocks swallow pipe errors, making broken output hard to diagnose. Unicode decoding depends on correct `-codec`. File transfer paths are minimally sanitized and operate relative to the connected share.

## Test Signals

Useful tests include mocked `ServiceInstall` install/uninstall/copy/delete paths, RemCom packet fields, pipe-open retry behavior, stdout/stderr buffering for prompt and newline boundaries, codec fallback warnings, keytab option mutation, command defaulting, and lab integration against a disposable Windows host validating service cleanup after success and failure.
