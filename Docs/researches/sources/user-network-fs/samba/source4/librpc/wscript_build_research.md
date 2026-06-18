# sources/user-network-fs/samba/source4/librpc/wscript_build

## Purpose

`wscript_build` defines the source4 librpc Waf build graph: Samba-specific NDR subsystems, grouping libraries, the core `dcerpc` client library, Python DCE/RPC extension modules, generated NDR table construction, and selected generated RPC client subsystems.

## Important APIs, Types, and Functions

The file uses Waf/Samba build declarations such as `bld.RECURSE()`, `bld.SAMBA_SUBSYSTEM()`, `bld.SAMBA_LIBRARY()`, `bld.SAMBA_PIDL_TABLES()`, `bld.SAMBA_PYTHON()`, `bld.SAMBA_SCRIPT()`, and `bld.INSTALL_FILES()`. Major targets include `NDR_IRPC`, `NDR_WINSIF`, `NDR_WINSREPL`, `ndr-samba4`, `dcerpc-samba4`, `ndr-table`, `RPC_NDR_IRPC`, `dcerpc-samr`, `dcerpc`, `pyrpc_util`, `python_dcerpc`, and many `python_*` generated modules.

## Control Flow

Waf evaluates this Python-like build script to recurse into IDL/tool directories, create generated NDR tables, define grouping libraries, build the core `dcerpc` library from the transport/auth/connect files, select warning-suppression flags for generated code, derive embedded Python utility library names, and declare generated Python modules with install names under `samba/dcerpc`.

## State and Persistence Behavior

It does not run application logic. Build state is represented in Waf's task graph and outputs generated/compiled artifacts. Installed Python module names and public headers are controlled here.

## Dependencies and Integration Points

This file binds together core libraries (`dcerpc`, `ndr`, `gensec`, SMB client libs, HTTP, credentials, tevent/talloc), generated NDR code, source3-generated SMBXSRV RPC code, and Python extension install layout. It is the integration point that ensures files in this work item are compiled into the expected libraries/modules.

## Risks and Test Signals

Risks include missing dependencies when a source starts using a new subsystem, generated module install-name drift, public header path conflicts, Python-build conditional mistakes, and grouping-library dependency omissions. Test signals are clean configure/build with Python enabled and disabled, generated NDR table freshness, import of every installed `samba.dcerpc.*` module, pkg-config/public header checks for `dcerpc`, and rebuilds after IDL changes.
