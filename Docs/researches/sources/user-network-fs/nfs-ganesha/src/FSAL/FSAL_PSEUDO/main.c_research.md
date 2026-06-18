# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/main.c

## Purpose
Registers the PSEUDO FSAL and defines its global capability defaults.

## Important APIs, Types, and Functions
Defines global `PSEUDOFS`, `init_config`, `unload_pseudo_fsal`, and `pseudo_fsal_init`.

## Control Flow
`pseudo_fsal_init` registers the FSAL as `PSEUDO`, installs export creation and unload ops, initializes handle ops, and displays fsinfo. Unload unregisters the module.

## State and Persistence Behavior
State is the global module object and capability flags. No persistent storage.

## Dependencies and Integration Points
Depends on FSAL init APIs, private FSAL declarations, and PSEUDO method declarations.

## Risks
No substantial config parsing occurs here. Registration failure is only printed. Some advertised capabilities, such as `cansettime`, exceed the narrow operation set implemented by handles.

## Test Signals
Successful registration, initialized handle ops, export creation, and clean unregister.
