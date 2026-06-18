<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/setfiles.c -->
# sources/security-integrity/selinux/policycoreutils/setfiles/setfiles.c

## Purpose
Implements both `setfiles` and `restorecon`, mapping their different command-line semantics onto libselinux restorecon operations.

## Important APIs, Types, And Functions
Important helpers are `usage()`, `set_rootpath()`, `canoncon()`, `audit_mass_relabel()`, and `log_callback()`. It configures global `r_opts`, `iamrestorecon`, `ctx_validate`, `policyfile`, `altpath`, `warn_no_match`, `null_terminated`, and `request_digest`. It uses libsepol policy validation, selinux callbacks, selabel stats/close, restore helpers, and optional libaudit `AUDIT_FS_RELABEL`.

## Control Flow
`main()` determines mode from `basename(argv[0])`. `setfiles` defaults to recursive, no realpath, association tracking, xdev, and eager context validation; `restorecon` defaults to nonrecursive, realpath, no association tracking, follows mounts, and exits silently if SELinux is disabled. Option parsing sets restorecon flags, exclusions, input-file mode, alternate root/specfile, policy validation source, digest behavior, and threads. It validates arguments, configures selabel options/callbacks, calls `restore_init()`, processes either `-f` input records or argv paths via `process_glob()`, optionally audits mass relabel, emits stats/counts, closes/free resources, and exits based on errors/skipped errors/relabeled count.

## State And Persistence
The command can relabel files, update directory digest xattrs, log to syslog, and emit audit records. In no-change mode it reports without mutating labels.

## Dependencies And Integration Points
It is the core backend for `restorecon`, `setfiles`, `fixfiles`, and build relabel targets.

## Risks And Edge Cases
Mode selection by argv0 is critical. `-f` input supports newline or NUL delimiting and can drive broad relabels. Alternate root rejects `/`. Policyfile validation exits on invalid contexts. Count-relabeled mode intentionally returns 1 when nothing changed.

## Test Signals
Cover argv0 mode differences, every option-to-flag mapping, input file delimiting, mass relabel audit, invalid contexts, alternate roots, excludes, digest behavior, thread counts, count-relabeled exit semantics, and SELinux-disabled restorecon behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/setfiles.c -->
