# sources/user-network-fs/impacket/examples/goldenPac.py

## Purpose

`goldenPac.py` is an MS14-068 exploitation example. It builds a forged PAC with elevated group SIDs, requests Kerberos tickets that include the forged authorization data, obtains a CIFS service ticket, logs into SMB with that ticket, and optionally executes a command through a RemCom/PSEXEC-style service workflow or writes the forged TGT to a ccache.

## Important APIs, Types, and Functions

`RemComMessage` and `RemComResponse` define pipe protocol structures. `PSEXEC.run()` installs or uploads a service executable, opens named pipes, sends command data, starts stdin/stdout/stderr pipe threads, waits for completion, uninstalls the service, and removes copied files. `Pipes`, `RemoteStdOutPipe`, `RemoteStdErrPipe`, `RemoteStdInPipe`, and `RemoteShell` implement the interactive pipe transport and file transfer commands.

`MS14_068` stores target, credentials, hashes, command/copy/write options, domain SID, forest SID, domain controllers, and KDC host. `getGoldenPAC(authTime)` builds `KERB_VALIDATION_INFO`, group memberships, optional forest enterprise admin SID, PAC client info, unkeyed MD5 checksums, and returns encoded authorization data. `getKerberosTGS()` injects that PAC as encrypted authorization data in a TGS-REQ and extracts the returned session key. `getForestSid()`, `getDomainControllers()`, and `getUserSID()` query NRPC, LSAT, DRSUAPI, and SAMR. `exploit()` orchestrates SID discovery, DC selection, vulnerable-ticket generation, CIFS TGS request, SMB Kerberos login, ccache write, and command execution.

## Control Flow

The CLI parses a target identity, command, optional upload file, optional ccache output, DC IP, target IP, and hashes. `exploit()` discovers the user SID and optionally the forest SID/domain controllers. For each candidate DC it requests a PAC-less TGT, decrypts the AS-REP to obtain `authTime`, creates a forged krbtgt TGS with the generated PAC, then requests `cifs/<target>`. Success breaks the loop; failure logs the DC as not vulnerable. On success it builds a TGS dictionary, authenticates SMB with `kerberosLogin(useCache=False)`, and invokes `PSEXEC` unless the command is `None`.

## State and Persistence Behavior

The script can persist a ccache through `-w`, install and remove a remote service, upload and delete a remote file, and execute remote commands. It also opens long-lived named pipes and changes local process state in `RemoteShell` commands such as `lcd`. Global variables such as `dialect` and `LastDataSent` coordinate pipe threads.

## Dependencies and Integration Points

It integrates with Kerberos, PAC, SAMR, LSAT, NRPC, DRSUAPI, SMB, SCM service installation, and Impacket RemCom service helpers. Many imports needed by class methods are performed only inside the `__main__` block, including `transport`, `samr`, Kerberos ASN.1 types, `MD5`, `NDRULONG`, and SAMR constants.

## Risks and Edge Cases

This is exploit code with invasive remote effects. Cleanup is best-effort; service uninstall or copied-file deletion can fail after partial execution. Imported use is fragile because several class methods depend on names imported only in `__main__`, and `PSEXEC` references `sys`, `transport`, `username`, and `domain` outside its constructor scope. Cryptographic behavior intentionally uses unkeyed PAC checksums for vulnerable DCs only. The stdout suppression check compares `LastDataSent > 10`, which is type-incorrect for bytes/strings versus integers. Broad exception handling can hide root causes and continue to the next DC.

## Test Signals

Most validation requires an isolated vulnerable lab. Unit tests can still cover PAC layout generation with fixed SID/RID/authTime, ccache write path mocking, DC selection fallbacks, and service cleanup on exceptions. Static/import tests should instantiate classes without running `__main__` to catch missing global imports. Integration tests should verify no service or uploaded file remains after success and failure.
