# sources/user-network-fs/cifs-utils/smb2-secdesc

## Purpose
`smb2-secdesc` is a Tk GUI helper for displaying the owner, group, DACL entries, and basic/advanced permission bits from a CIFS file security descriptor.

## Important APIs, types, and functions
The script uses `CIFS_QUERY_INFO = 0xc018cf07`, opens a target file, requests security info with owner/group/DACL bits, and decodes binary structures with `struct`. `SID`, `ACE`, `ACL`, and `SecurityDescriptor` model MS-DTYP structures. `App` builds a Tkinter UI with owner/group labels, an ACE list, and disabled checkbuttons for basic and advanced permission interpretation.

## Control flow
`main` requires a single filename, allocates a 16 KiB buffer, packs `InfoType: Security`, `AddInfo: Group/Owner/Dacl`, and input length, runs the ioctl, decodes the returned security descriptor, then starts a Tk event loop. Selecting ACEs updates the displayed permission checkbuttons.

## State and persistence behavior
The tool is read-only. It stores decoded descriptor data only in memory and does not modify server ACLs or local files.

## Dependencies and integration points
It depends on Linux CIFS ioctl support, Python GUI bindings, and a display environment. It overlaps functionally with `smbinfo secdesc` and `getcifsacl`, but presents a GUI view instead of text output.

## Risks
The file is Python 2 style despite a modern tree containing Python 3 utilities: it imports `Tkinter` and uses `print` statements without parentheses. On current Python 3 systems it will fail unless converted. There is little bounds checking for malformed descriptors. The UI maps only ACE types 0 and 1 for most views and ignores editing. One advanced checkbox appears wrong: `CHAN_PERM` updates `bf_adv_rp` instead of the change-permissions checkbox. The listbox width calculation uses `if max > len(sid)` rather than the likely intended less-than comparison.

## Test signals
Run syntax checks under the intended Python version, GUI smoke tests with Xvfb, descriptor decoding tests with synthetic owner/group/DACL buffers, and live ioctl tests on files and directories. Compare displayed flags against `smbinfo secdesc` for the same object.
