# sources/user-network-fs/davfs2/man/de/umount.davfs.8.po.in

## Purpose
This PO input provides the German translation for `umount.davfs(8)`, the unmount helper manual.

## Important APIs and structure
It preserves placeholders such as `u@PROGRAM_NAME@`, `@PACKAGE@`, `@SYS_RUN@`, and references shared section translations from other davfs2 manpages. It documents `u@PROGRAM_NAME@`, `umount dir`, version/help options, ignored compatibility options `-f -l -n -r -v -t`, PID-file lookup under `@SYS_RUN@`, and see-also references.

## Control flow described
The manual explains that the helper is called by `umount(8)` and waits until `mount.davfs` has synchronized cached files to the WebDAV server. It advises `umount -i` if the daemon has serious errors and the helper cannot complete.

## State and persistence behavior
The documented state is cached dirty data pending upload and PID files for running davfs processes. Correct unmount behavior affects whether local cache changes have been synchronized before command return.

## Dependencies and integration points
It is installed through German manpage build rules and must align with the `u@PROGRAM_NAME@` helper, `umount(8)` behavior, runtime PID directory, and mount documentation.

## Risks
The header copyright line contains `2914`, likely a typo for 2014. The PO revision is much older than the POT creation date, so source drift should be reviewed even though this file is much smaller than mount/config translations. Misdocumentation here can lead users to bypass synchronization with `umount -i` without understanding data-loss implications.

## Test signals
Run msgfmt/po4a validation, build the rendered manpage, check placeholders, and verify option text against the actual unmount helper parser. Include translation freshness checks when English unmount documentation changes.
