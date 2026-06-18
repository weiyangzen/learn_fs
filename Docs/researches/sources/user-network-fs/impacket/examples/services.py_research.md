# sources/user-network-fs/impacket/examples/services.py

## Purpose

`services.py` manipulates Windows services over the Service Control Manager Remote Protocol. It can list services, query status/configuration, start, stop, delete, create, or change a service.

## Important APIs, Types, and Functions

`SVCCTL` stores credentials, Kerberos settings, selected action, and SMB port. `run()` creates an `ncacn_np:<remote>[\pipe\svcctl]` transport and configures auth. `doStuff()` binds SCMR, opens the service control manager, optionally opens a service, dispatches the requested action, encrypts service account passwords with `encryptSecret()` for change operations, closes handles, and disconnects.

## Control Flow

The CLI defines subcommands for `start`, `stop`, `delete`, `status`, `config`, `list`, `create`, and `change`, then parses auth and connection settings. `doStuff()` opens SCM, branches on `self.__action`, and calls the corresponding `scmr.hR*` helper. Read operations print decoded state/config. Mutating operations call start/stop/delete/create/change and close service handles when implemented.

## State and Persistence Behavior

Start/stop affect service runtime state. Delete, create, and change persistently alter SCM configuration. Changing a service account password encrypts the password with the SMB session key before transmission. The script writes no local files.

## Dependencies and Integration Points

It depends on Impacket `transport`, `scmr`, NDR `NULL`, `encryptSecret`, target parsing, Kerberos/AES/hash support, and SMB named-pipe transport on ports 139/445.

## Risks and Edge Cases

Service operations are high impact and can break hosts. Error handling is mostly outer-level; the file TODO notes error checking is incomplete. Handles may not close if an exception occurs before the close calls. `CREATE` does not close a returned service handle. Numeric service/start types are accepted as raw integers with little validation. Password arguments can leak through shell history.

## Test Signals

Mock tests should verify action dispatch, SCMR calls, state label rendering, config rendering, password encryption invocation, and close/disconnect behavior. Integration tests should run against disposable services on a lab Windows host for all subcommands and auth modes.
