# sources/user-network-fs/samba/source3/smbd/notifyd/wscript_build

## Purpose
This waf build fragment defines the notifyd-related subsystems, helper binaries, and torture module for Samba's source3 build.

## Important APIs, Types, and Functions
It declares `fcn_wait`, `notifyd_db`, and `notifyd` as `SAMBA3_SUBSYSTEM`s. It declares non-installed binaries `notifyd-tests` and `notifydd`. It sets `TORTURE_NOTIFYD_SOURCE` and `TORTURE_NOTIFYD_DEPS`, then declares the internal `TORTURE_NOTIFYD` smbtorture module with init function `torture_notifyd_init`.

## Control Flow
The build graph compiles `fcn_wait.c` separately, builds `notifyd_db` from `notifyd_entry.c notifyd_db.c`, builds `notifyd.c` with db/messaging dependencies, and compiles optional test executables. The torture module is enabled when Python build support is enabled.

## State and Persistence
The file defines build metadata only. It does not create runtime state, but its dependency choices determine which symbols are linked into tests and binaries.

## Dependencies and Integration Points
Key dependencies include `samba3core`, `samba-debug`, `dbwrap`, `errors3`, `util_tdb`, `TDB_LIB`, `messages_util`, `smbconf`, `fcn_wait`, and `notifyd_db`. It ties the C files in this folder into Samba's larger build and test systems.

## Risks and Edge Cases
If dependencies are incomplete, failures may appear only in selected build configurations, especially the internal torture module. `notifyd-tests` depends only on `smbconf` here even though its source includes messaging and notifyd headers; transitive availability must remain valid.

## Test Signals
Successful build of the subsystems, non-installed binaries, and `TORTURE_NOTIFYD` module is the primary signal. Running the torture suite confirms that the declared init function and dependencies are correct.
