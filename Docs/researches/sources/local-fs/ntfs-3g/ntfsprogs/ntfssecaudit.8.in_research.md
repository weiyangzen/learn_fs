# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfssecaudit.8.in

## File Role

`ntfssecaudit.8.in` is the manual page template for the `ntfssecaudit` administrative tool. It documents NTFS security data auditing, ACL backup/restore, permission display and modification, and user-mapping proposal generation.

The file is roff/manpage source for section 8. It is documentation only, not executable code.

## Documented Command

The command is:

`ntfssecaudit [options] args`

The manpage describes `ntfssecaudit` as a terminal-only utility for displaying file ownership and permissions on NTFS filesystems and checking their consistency.

When a volume argument is required, the volume must be unmounted and the command must be run as root. The volume may be a block device or an image file. Mounted-file modes are special cases that do not require root.

## Options Summary

The synopsis lists these option letters:

- `-a`: full auditing of security data on Linux
- `-b`: backup ACLs
- `-e`: set extra backed-up parameters with `-s`
- `-h`: display hexadecimal security descriptors saved in a file
- `-r`: recurse into a directory
- `-s`: set backed-up ACLs
- `-u`: generate a user mapping proposal
- `-v`: verbose output, very verbose when specified twice

The manpage notes that running the command with no args displays a summary of options.

## Valid Invocation Forms

The manpage is structured around valid option/argument combinations:

- `-h file`: display saved hexadecimal security descriptors in human-readable form.
- `-a[rv] volume`: audit global security data on a volume; with `-r`, also scan files and directories and check their relation to global security data.
- `[-v] volume file`: display security parameters for a file on an unmounted volume.
- `-r[v] volume directory`: display security parameters recursively for a directory on an unmounted volume.
- `-b[v] volume [directory]`: recursively write NTFS ACL backup data to standard output.
- `-s[ev] volume [backup-file]`: restore NTFS ACLs from a backup file or standard input; `-e` also restores extra parameters, currently Windows attributes.
- `volume perms file`: set one file’s security parameters.
- `-r[v] volume perms directory`: recursively set security parameters for a directory tree.
- `[-v] mounted-file`: display security parameters for a mounted file or directory without root.
- `-u[v] mounted-file`: generate proposed user mapping content based on ownership from a Windows-created mounted file.

All mandatory arguments must be unique. If shell wildcards are used, they must resolve to a single name.

## Permission and ACL Semantics

Displayed security information includes:

- interpreted Linux mode in octal rwx form
- POSIX ACL, if POSIX ACL support was selected at compile time
- NTFS security key, if present
- security descriptor in verbose output

For setting permissions, `perms` may be either:

- a Linux mode in octal form, as with `chmod`
- a POSIX ACL expression, as with `setfacl -m`

The manpage states that new ACLs set by the tool are effective for both Linux and Windows.

The POSIX ACL note defines the supported ACL syntax as `[d:]{ugmo}:[id]:[perms],...`, where `id` is numeric user/group ID and `perms` is either an octal digit or letters from `r`, `w`, and `x`.

## User Mapping Workflow

The `-u[v] mounted-file` mode prints proposed contents for `.NTFS-3G/UserMapping`. It assumes the mounted file was created on Windows by the user who should map to the current Linux user.

The user is expected to place the generated content into the hidden `.NTFS-3G/UserMapping` file at the root of the target partition. That mapping causes files created on that partition to receive ownership corresponding to the original Windows identity.

## Audit and Repair Guidance

The `-a[rv] volume` audit mode scans global security data and optionally scans all files/directories. It is not effective on pre-NTFS-3.0 volumes because old NTFS versions have no global security data.

If errors are reported, the manpage advises repairing the volume with an appropriate tool such as Windows `chkdsk`.

The description warns that directory or volume operations may produce large output, so output redirection or piping to a text editor is recommended.

## Examples

The examples cover:

- auditing global security data on `/dev/sda1` with `ntfssecaudit -ar /dev/sda1`
- displaying ownership and permissions for `/audio/music` on `/dev/sda5`
- recursively setting files in `/audio/music` on `/dev/sda5` to mode `644`

## Exit Codes

The documented exit behavior is simple:

- `0`: no error detected
- `1`: an error was detected

## Cross References and Project Metadata

The manpage points known issues to the NTFS-3G FAQ on GitHub and lists the ntfs-3g development mailing list for reporting new issues.

Authors and thanks sections credit Jean-Pierre André as the tool author and acknowledge major ntfs-3g contributors.

See-also references:

- `ntfsprogs(8)`
- `attr(5)`
- `getfattr(1)`

## Summary

`ntfssecaudit.8.in` documents an administrative NTFS ACL/security auditing utility. It defines the supported command forms for auditing, displaying, backing up, restoring, and setting NTFS security descriptors and Linux-interpreted permissions. The document is especially important for understanding root/unmounted-volume requirements, mounted-file exceptions, POSIX ACL syntax, user mapping generation, and expected exit codes.
