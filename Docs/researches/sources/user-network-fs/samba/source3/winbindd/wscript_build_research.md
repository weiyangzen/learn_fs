<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wscript_build -->
# sources/user-network-fs/samba/source3/winbindd/wscript_build

## Purpose
This Waf build script defines the Samba3 winbindd/idmap/nss_info build graph. It declares idmap libraries/modules, nss_info modules, optional varlink support, the core `winbindd-lib` subsystem, and the `winbindd` binary.

## Important APIs, Types, And Functions
The file uses Waf helpers such as `bld.SAMBA3_LIBRARY`, `bld.SAMBA3_SUBSYSTEM`, `bld.SAMBA3_MODULE`, and `bld.SAMBA3_BINARY`. The important targets in this subset are `VARLINK`, `winbindd-lib`, and `winbindd`, plus idmap and nss_info module targets.

## Control Flow
Build declarations are evaluated by Waf. Module enablement is conditional on configured static/enabled module state, LDAP availability, `with_systemd_userdb`, and `build_winbind`. `VARLINK` compiles the four varlink sources only when systemd userdb support is enabled. `winbindd-lib` aggregates the core winbindd C sources and depends on `VARLINK`, RPC, idmap, passdb, ADS, messaging, and related subsystems. `winbindd` links `winbindd.c` against `winbindd-lib`.

## State And Persistence Behavior
There is no runtime state. Build state is generated artifacts, enabled module selections, and install output under `${SBINDIR}` for the binary.

## Dependencies And Integration Points
It integrates winbindd with Samba's broader build system, idmap plugin loading model, nss_info plugin model, optional varlink/systemd support, and the Samba3 binary installation path.

## Risks And Test Signals
Risks include missing source/dependency entries when files are added, optional varlink code not compiling unless `with_systemd_userdb` is exercised, LDAP-gated modules silently dropping from builds, and broad `winbindd-lib` dependency churn. Test signals are configuration/build matrix coverage for static and shared modules, LDAP on/off, systemd userdb on/off, and `build_winbind` enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wscript_build -->
