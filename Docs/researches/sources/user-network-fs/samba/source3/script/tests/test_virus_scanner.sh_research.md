# sources/user-network-fs/samba/source3/script/tests/test_virus_scanner.sh

Purpose: blackbox validation of the `vfs_virusfilter` behavior for infected and healthy files on read and write paths. It checks that infected paths are renamed using the configured prefix/suffix and are not transferred, while healthy files round-trip correctly.

Important functions and APIs: uses `smbclient`, selftest `USER`/`PASSWORD`, and subunit. `check_infected_read()` creates a nested `infected.txt`, attempts `get`, and expects `virusfilter.infected.txt.infected` to exist with no downloaded copy. `check_infected_write()` uploads a non-empty infected source and expects `virusfilter.infected.upload.txt.infected`. `check_healthy_read()` and `check_healthy_write()` use `cmp` to verify content integrity.

Control flow: each check starts by clearing the share directory, prepares the fixture, invokes `smbclient`, validates filesystem side effects, and returns a subunit result. The four checks run sequentially.

State and persistence: repeatedly removes contents of `${LOCAL_PATH}/${SHARE}` and creates test files below it. It leaves healthy-write artifacts until the next check or environment cleanup.

Dependencies and integration: registered as `samba3.blackbox.virus_scanner` in `fileserver:local`. It assumes the share `virusfilter` has a scanner fixture that treats names containing `infected` as positive detections and performs configured rename-on-infection behavior.

Risks and test signals: the test does not inspect smbclient exit status for infected transfers, relying on filesystem effects instead. Strong signals are renamed infected files, absence of transfer artifacts, and byte-for-byte healthy file comparisons.
