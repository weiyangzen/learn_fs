# File Research: sources/virtualization/nvme-cli/plugins/innogrit/innogrit-nvme.c

This file implements the Innogrit nvme-cli plugin commands registered in `innogrit-nvme.h`: `get-eventlog` and `get-cdump`.

Main behavior:
- Provides `nvme_vucmd()` as a generic Innogrit vendor admin passthrough helper. It sets the vendor signature `IGVSC_SIG` in `cdw2`, sets namespace to all namespaces, uses `data_len / 4` in `cdw10`, and sends the command through `libnvme_exec_admin_passthru()`.
- Provides `getlogpage()` as a wrapper around `nvme_init_get_log()` and `libnvme_get_log()`, adding the log-specific `LSP` field into `cdw10`.
- Detects vendor command style with `getvsctype()`, trying log page `0xe1` first and falling back to vendor opcode `0xfe`; a `drvinfo_t.signature == 0x5A` indicates type 1 handling.
- `getvsc_eventlog()` retrieves event logs via vendor-specific commands. It handles two command layouts depending on `getvsctype()`, validates `EVLOG_SIG`, tolerates up to 16 invalid chunks, writes 4 KiB chunks to a file, and stops when the tail marker `0xffffffff00000000` is observed.
- `getlogpage_eventlog()` retrieves event logs via log page `0xcb` with LSP selectors. It probes support with selector `0x01`, retrieves total-size metadata with selector `0x02`, then pulls data with selector `0x00`.
- `innogrit_geteventlog()` opens the device, creates a timestamped `eventlog_MMDD-HHMMSS.eraw` file in the current working directory, tries the log-page path first, falls back to VSC retrieval on `IG_UNSUPPORT`, and chmods the output to `0666`.
- `innogrit_vsc_getcdump()` retrieves controller dump data. It first attempts Innogrit VSC dump metadata and supports multiple cdump packs with firmware-version-labeled filenames. If VSC metadata is unavailable, it falls back to standard log page `0x07`. It writes `cdumpstart` and `cdumpend` markers around raw dump payloads.

Important data dependencies:
- Uses constants and structures from `typedef.h`: `IGVSC_SIG`, `SRB_SIGNATURE`, `EVLOG_SIG`, `drvinfo_t`, `evlg_flush_hdr`, and `cdumpinfo`.
- Depends on nvme-cli helpers: `parse_and_open()`, cleanup attributes, `nvme_get_nsid_log()`, and libnvme passthrough helpers.

Notable quirks:
- `getlogpage()` accepts a `result` pointer but does not pass it to `libnvme_get_log()` or fill it. `getlogpage_eventlog()` expects `result` to contain total pages after selector `0x02`, so that path appears ineffective unless libnvme mutates state outside the visible argument.
- In `innogrit_vsc_getcdump()`, after advancing to the next VSC pack, it recomputes `fname` but reopens `filename` without updating it from `fname`; this can append later packs to the previous path.
- File creation uses `sprintf()` into fixed buffers and `fopen(..., "a+")`, so repeated timestamps or long current directories may behave poorly.
