# File Research: sources/virtualization/nvme-cli/ccan/meson.build

- Purpose: Meson build definition for bundled CCAN static library.
- Sources: includes hash, htable, ilog, likely, list, str debug/string, and strset C files.
- Debug behavior: debug build type adds `-DCCAN_LIST_DEBUG=1` and `-DCCAN_STR_DEBUG=1`.
- Output: builds non-installed static library `ccan` and exposes `ccan_dep` with include directory and `config_dep`.
