# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-internal-logs.c

Solidigm internal/debug log collection implementation. It can dump vendor NLOG/event/assert logs, standard telemetry logs, identify pages, persistent event log, and selected standard/vendor log pages into a timestamped directory that is then zipped.

Public command:
- `solidigm_get_internal_log`: parses `--type` and `--dir-name`, creates `<serial>-YYYYMMDDHHMMSS`, collects requested logs, compresses with `zip`, and removes the raw folder on successful compression.

Supported types:
- `ALL`
- `HIT`
- `CIT`
- `NLOG`
- `ASSERT`
- `EVENT`
- `EXTENDED`

Vendor dump path:
- Uses admin passthrough opcode `0xd2`.
- `cmd_dump_repeat` transfers up to 4096 bytes per command, tracks dword offsets in CDW13, and optionally forces max transfer size in CDW10.
- `ilog_dump_nlogs`: iterates selected core and NLOG number, writes `NLog.bin`.
- `ilog_dump_assert_logs`: reads assert header, writes valid core assert sections to `AssertLog.bin`.
- `ilog_dump_event_logs`: reads event header and per-core event sections to `EventLog.bin`.

Standard/extended dump path:
- `ilog_dump_telemetry`: uses Solidigm dynamic telemetry helper for host-initiated or controller-initiated telemetry. It enables extended telemetry data area support through host behavior feature when needed and restores previous host behavior afterward.
- `ilog_dump_identify_pages`: saves controller, namespace, namespace descriptor, CSI, allocated namespace, namespace controller list, active/allocated namespace lists, NVM set list, controller list, etc.
- `ilog_dump_no_lsp_log_pages`: saves many standard and vendor log pages without LSP, including SMART, error, firmware slot, changed namespace, command effects, sanitize, OCP/VU pages, SMART attributes, temperature stats, and latency outlier.
- `ilog_dump_pel`: releases/establishes persistent event log context, reads full PEL, saves it, then releases context.

Important helpers:
- `get_serial_number`: identifies controller and trims trailing spaces in serial.
- `ilog_ensure_dump_id_ctrl`: caches and dumps identify controller once.
- `is_atmos`: detects model prefix `SOLIDIGM SB5`.
- `get_max_da`: chooses telemetry data area based on model and identify-controller LPA bits.
- `log_save`: creates subdirectories and writes full buffers.
- `ensure_dir`: creates subdirectories if missing.

Notable issues:
- `ensure_dir` calls `mkdir(file_path, 777)`, using decimal `777` rather than octal `0777`.
- Shell commands are assembled for `zip` and `rm -rf`; `zip` command quotes paths, but cleanup command does not quote `cfg.out_dir`.
- `ilog_dump_pel` calls `nvme_get_log_persistent_event` with `pevent == NULL` before allocation, then allocates and repeats; this first call is suspicious.
- `ilog_dump_log_page` ignores its `nsid` parameter and passes namespace ID `0` to `nvme_get_nsid_log`.
- `cmd_dump_repeat` treats short positive `write` counts as success and does not retry partial writes.
- The code continues after many collection failures and reports total successful files, which is appropriate for best-effort debug collection but means command success can mask missing log classes.

Storage relevance:
- Captures the diagnostic state needed for NVMe device failure analysis, including controller/namespace identify data, persistent event logs, telemetry, and vendor firmware logs. These artifacts are important when correlating filesystem/block-layer failures with drive firmware or media state.
