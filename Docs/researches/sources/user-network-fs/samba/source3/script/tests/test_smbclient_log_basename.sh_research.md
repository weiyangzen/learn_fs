# sources/user-network-fs/samba/source3/script/tests/test_smbclient_log_basename.sh

## Purpose
This script verifies that `smbclient -l <log-basename>` creates and writes to the expected log file even when authentication fails.

## Important APIs, Functions, and Control Flow
It accepts `SERVER SMBCLIENT PREFIX` plus extra args, loads `subunit.sh`, and defines `$LOG_DIR=$PREFIX/st_log_basename_dir`. `test_smbclient_log_basename` recreates the directory, runs `$VALGRIND $SMBCLIENT -l $LOG_DIR -d3 //$SERVER/IPC$ $CONFIGURATION -U%badpassword -c quit $ADDARGS`, and greps `$LOG_DIR/log.smbclient` for `Client started`.

## State, Dependencies, Integration, and Risks
State is a log directory under `$PREFIX`. The command intentionally uses bad credentials, so the useful signal is log creation, not login success. It depends on `$CONFIGURATION` being available from the caller and on debug logging format. Risks include stale log files if directory cleanup fails and false failures if the startup log string changes.
