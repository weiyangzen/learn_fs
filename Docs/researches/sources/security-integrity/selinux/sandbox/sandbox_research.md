# sources/security-integrity/selinux/sandbox/sandbox
# sources/security-integrity/selinux/sandbox/sandbox

Purpose: Python CLI wrapper that launches commands, X apps, Wayland apps, or sessions in an SELinux sandbox context, optionally with private home/tmp/runtime directories.

Important APIs and control flow: top-level helpers handle signals, errors, file copy/save, MCS category reservation via abstract UNIX sockets, range parsing from current context, MCS pair generation, and PATH resolution. `Sandbox.__parse_options()` defines options for includes, type, mount, DPI, session, shredding, X/Wayland, alternate home/tmp/runtime dirs, window size/manager, MLS/MCS level, and capabilities. `__gen_context()` derives exec/file contexts. `__setup_dir()` creates/chcons private dirs and copies included files. `__execute()` either invokes setuid `seunshare` for mounted/X/Wayland mode or forks directly with `selinux.setexeccon()` for simple command mode, then saves modified included files and removes temporary dirs.

State and persistence: creates temporary sandbox home/tmp/runuser directories under `/tmp`, `.sandboxrc`, copied included files, optional saved changes back to originals, MCS reservation sockets, and SELinux contexts. Cleanup removes temp dirs unless caller supplied them.

Dependencies and integration points: depends on `selinux`, `sepolicy`, `seunshare`, `sandboxX.sh`, Gtk for dialogs/DPI, `xmodmap`, `dbus-run-session`, `dbus-launch`, and SELinux sandbox policy.

Risks and test signals: security depends on correct MCS category allocation, context construction, and safe cleanup. There is a likely cleanup bug: when shredding tmpdir it calls `self.shred(self.__homedir)` instead of `self.__tmpdir`. Tests in `test_sandbox.py` cover basic sandbox restrictions and mount options under enforcing SELinux.
