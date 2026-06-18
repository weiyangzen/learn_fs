# File Research: sources/virtualization/guestfs-tools/df/main.c

## Scope

Command-line front end and guest selection logic for `virt-df`.

## CLI And Modes

- Supports disk/domain selection, libvirt URI, format/blocksize, CSV, human-readable, inode mode, UUID output, thread count, verbosity/version/trace, and legacy `--one-per-guest`.
- Supports old-style syntax by inferring disk paths or domain names from positional arguments when no `-a`/`-d` was given.
- Rejects extra arguments and `-h` combined with `--csv`.
- If no drives are specified, enumerates all libvirt domains and runs `df_work` through `start_threads`.
- If drives are specified, treats them as one guest, launches a single handle, synthesizes a display name, and calls `df_on_handle`.

## Display Name Logic

- Single drive names come from basename, URI final path element, or domain name.
- Multiple drives use the last list item’s name plus one `+` per additional disk.

## Dependencies And Risks

- All-domain mode requires libvirt.
- Single `-d` mode lacks UUID because the libvirt domain handle is hidden inside guestfs add-domain.
- Shared globals are consumed by options and output code.
