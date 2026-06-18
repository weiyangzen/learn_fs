# File Research: sources/virtualization/guestfs-tools/cat/cat.c

## Scope

Implements `virt-cat`, a read-only tool that prints files from virtual machine disk images or domains.

## CLI And Mounting

- Supports `-a`, `-d`, `-c`, `--format`, `--blocksize`, LUKS key options, `-m`, verbose/version/trace/help, and long/short option discovery.
- Defaults to inspector mode and read-only operation.
- Supports old-style syntax by inferring disk images or domain names from positional arguments before the final file path.
- If `-m` is supplied, disables inspector and uses explicit mountpoints.
- Adds drives, enables network if key store requires it, launches libguestfs, then either mounts explicit mountpoints or auto-inspects/mounts the guest.

## File Output

- Requires at least one guest file path.
- In inspector mode, obtains the single root and detects Windows.
- For Windows guests, converts requested paths through `windows_path`.
- Streams each requested file to stdout via `guestfs_download(filename, "/dev/stdout")`.
- Returns failure if any requested file cannot be converted or downloaded.

## Dependencies And Risks

- Assumes inspector finds exactly one root when used.
- Windows path conversion is read-only.
- Output is raw file content; multiple requested files are concatenated without delimiters.
