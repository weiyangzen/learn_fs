# sources/test-tools/kdevops/scripts/honey-badger.py

## Purpose
This Python tool discovers Ubuntu mainline kernel builds, lists recent stable versions, downloads the image/modules/headers `.deb` packages, and installs or extracts them. It supports Debian systems through `dpkg` and non-Debian or alternate roots through manual `ar` plus tar extraction.

## Important APIs, Types, And Functions
`KERNEL_PPA_URL`, `ARCH`, and `KERNEL_DIR` define the source and local cache. `is_dpkg_installed()` probes `dpkg`. `parse_version()` parses `vX.Y[.Z][-rcN]` into a sortable tuple. `get_kernel_versions()` fetches the index with `requests`, parses links via BeautifulSoup, sorts them, and calls `group_versions()` to group by major/minor. `verify_kernel_files()` checks whether a version has both `linux-image-unsigned` and `linux-modules` packages. `download_and_install()` downloads matching `.deb` files and delegates to `install_kernel_packages()`. `extract_deb()` manually unpacks the `ar` archive and extracts `data.tar*`.

## Control Flow
`main()` parses CLI options, discovers grouped versions, takes the latest candidate per major/minor group until `--count` valid versions are found, lists them if `--list`, installs a supplied `--use-file` package if requested, or downloads `linux-modules`, `linux-image-unsigned`, and `linux-headers` packages for each valid version. `--dest` is passed to manual extraction.

## State And Persistence
Network state comes from `https://kernel.ubuntu.com/mainline/`. Downloaded packages are persisted in `/tmp/kernels`. Installation mutates the host through `sudo dpkg -i` or writes extracted package payloads into `dest`, defaulting to `/`. Temporary manual extraction directories are removed.

## Dependencies And Integration Points
It requires `requests`, `bs4`, `ar`, `tarfile`, filesystem write access, and optionally `sudo dpkg`. It integrates with kdevops workflows that need quickly available stable kernels for testing.

## Risks And Test Signals
The `--use-ar` default is set to `dpkg_installed`, despite the help text saying "Do not use dpkg even if present", which means systems with dpkg default to manual extraction rather than `dpkg`; that is worth verifying. `tar.extractall()` extracts archive paths without filtering, so untrusted `.deb` content is a path traversal risk. Downloads use `r.content`, loading entire packages into memory. `--dest` can be `None` in the `--use-file` path, which later reaches tar extraction as the extraction path. Test with mocked HTTP indexes, temporary kernel directories, a fake `.deb`, and both dpkg/manual code paths.
