# File Research: sources/virtualization/nvme-cli/nvme.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9504, source bytes 262124, report `Docs/researches/chunks/chunk_sources_virtualization_nvme_cli_nvme_c_1_1_9504_4e0556111f34_research.md`
- chunk 2: lines 9505-11419, source bytes 48111, report `Docs/researches/chunks/chunk_sources_virtualization_nvme_cli_nvme_c_2_9505_11419_e8317836987b_research.md`

## Chunk Research

### Chunk 1: lines 1-9504

# Chunk Research: sources/virtualization/nvme-cli/nvme.c lines 1-9504

## Scope

This chunk covers the beginning through most of the generic passthrough implementation of `nvme.c`. It defines the built-in `nvme` CLI program object, common option/config structures, shared open/parse helpers, and a large set of built-in command handlers for identify, logs, namespace management, firmware, controller registers/properties, format/sanitize, feature get/set, security/directive commands, core I/O commands, reservations, and the start of arbitrary admin/I/O passthrough.

The chunk ends at line 9504 inside `passthru()`, immediately after data-buffer allocation/prefill and before the rest of passthrough command construction/execution. The file tail after this range contains cross-chunk continuations for passthrough wrappers, NVMe-oF host/key/TLS commands, fabrics connect/discover commands, NVMe-MI helpers, additional log readers, extension registration, and `main()`.

## Program and Shared State

- Built-in command registration is created via `CREATE_CMD` plus `nvme-builtin.h`, then wrapped in `builtin` and `nvme`.
- Shared CLI state lives in `struct nvme_args nvme_args`, including output format, timeout, verbosity, dry-run, and ioctl-probing behavior.
- Main reusable config structs in this range: `feat_cfg`, `passthru_config`, `get_reg_config`, and `set_reg_config`.
- Most command handlers use cleanup attributes for libnvme allocations, global contexts, transport handles, file descriptors, and huge allocations.

## Control Flow and APIs

- `parse_and_open()` is the standard command prologue: parse options, create libnvme context, configure ioctl probing, open the transport handle, install submit/retry hooks, apply dry-run and timeout.
- `open_fallback_chardev()` reopens controller handles as `/dev/<ctrl>n<nsid>` for namespace I/O commands.
- `validate_output_format()` maps `normal`, optional `json`, `binary`, and `tabular` to print flags.
- The command body pattern is usually: parse/open, validate output, derive namespace/controller state, allocate buffers, initialize command, execute through libnvme, print via `nvme_show_*`.

## Command Families

- Log commands cover SMART, ANA, telemetry, endurance, command effects, supported logs, error, firmware, changed namespace lists, predictable latency, persistent event, LBA status, reservation notification, boot partition, PHY RX EOM, media unit, capacity config, sanitize, FID effects, and MI command effects.
- Identify/list commands cover controllers, namespaces, command sets, UUIDs, NVM sets, domains, primary/secondary controller virtualization capabilities, topology list, subsystem list, and `top`.
- Namespace management includes create/delete/attach/detach, with `create_ns()` deriving FLBAS, namespace granularity, SI sizes, ZNS fields, placement handles, and issuing namespace management passthrough.
- Firmware and destructive maintenance include firmware download/commit, reset/subsystem reset/rescan, sanitize, sanitize namespace, and format.
- Register/property handling chooses MMIO mapping when possible and falls back to NVMe fabrics Get/Set Property.
- Feature handling supports feature iteration, changed/default comparison, feature payload buffers, timestamp convenience encoding, and set-feature payload reads.
- I/O paths include write zeroes, write uncorrectable, DSM, copy, flush, reservations, read/write/compare through `submit_io()`, verify, security send/receive, directives, lockdown, and RPMB handoff.
- Generic passthrough starts at the end of the chunk, parsing opcode/CDWs/data/metadata/read/write/raw/show/latency options and allocating buffers before the chunk boundary.

## Dependencies

- Heavy dependence on libnvme transport handles, topology scanning, identify/log/feature helpers, raw admin and I/O passthrough, status helpers, huge memory allocation, resets, namespace operations, fabrics properties, and optional NVMe-MI endpoints.
- Local dependencies include `util/argconfig.h`, `nvme-cmds.h`, `nvme-print.h`, `logging.h`, `util/suffix.h`, `util/sighdl.h`, `util/cleanup.h`, and `malloc.h`.
- Platform dependencies include Linux NVMe device nodes, `/sys/class/nvme/.../resource0`, POSIX file I/O, `mmap`, `fsync`, `fstat`, and compile-time `CONFIG_JSONC`, `CONFIG_MI`, `NVME_HAVE_MMAP`.

## Risks and Edge Cases

- `get_transport_handle()` accepts `flags` but does not use them, so `open_exclusive()` appears not to enforce `O_EXCL` in this visible path.
- `is_ns_mgmt_support()` appears inverted: it returns false on successful allocation and would identify through a null pointer if allocation failed.
- `get_feature_id()` allocates `data_len - 1` but passes `data_len` to `nvme_get_features()`.
- `get_feature_id_changed()` uses `strcmp()` on binary buffers and appears to print when current/default buffers are equal.
- `sec_send()` can read more bytes than the allocated transfer buffer when the file is larger than `--tl`.
- `submit_io()` returns the current `err` for invalid `prinfo > 0xf`, often meaning success.
- Some file-output paths do not robustly handle short writes.
- Several user-controlled lengths allocate large buffers directly.
- Destructive commands rely on mixed validation, prompts, and intended exclusivity; automation should treat format/sanitize/write/register/namespace/firmware paths as hardware state-changing.

## Cross-Chunk References

- `passthru()` continues after line 9504 and must be completed by the next chunk.
- Later chunks implement `io_passthru()`, `admin_passthru()`, host NQN/key/TLS commands, fabrics discover/connect/disconnect/config/DIM, NVMe-MI helpers, late log commands, `register_extension()`, and `main()`.
- Helpers defined here are used later: `nvme_args`, `validate_output_format()`, `parse_and_open()`, `open_exclusive()`, `put_transport_handle()`, `get_reg_size()`, `nvme_is_ctrl_reg()`, and `elapsed_utime()`.

### Chunk 2: lines 9505-11419

# Chunk Research: sources/virtualization/nvme-cli/nvme.c lines 9505-11419

## Scope

This chunk is the tail of `nvme.c`. It completes the generic passthrough implementation started before line 9505, then defines CLI handlers for host identity generation, DH-HMAC-CHAP and TLS PSK key management, topology display, NVMe-oF wrapper commands, optional NVMe-MI passthrough, several newer log-page readers, extension registration, and `main()`.

Adjacent context used: `passthru()` and `passthru_print_read_output()` begin at lines 9327-9504, and `nvme-builtin.h` registers the handlers in this range as builtin commands.

## APIs And Entry Points

- `io_passthru()` / `admin_passthru()` (9585-9599): thin wrappers over `passthru(argc, argv, admin, desc, acmd)`, selecting IO vs admin passthrough.
- `gen_hostnqn_cmd()` / `show_hostnqn_cmd()` (9601-9633): call `libnvme_generate_hostnqn()` and/or `libnvme_read_hostnqn()` and print the selected host NQN.
- `gen_dhchap_key()` / `check_dhchap_key()` (9636-9839): generate and validate NVMe in-band authentication DH-HMAC-CHAP keys using libnvme raw-secret helpers, base64 utilities, and CRC32.
- `append_keyfile()` (9841-9910): helper that resolves a keyring, describes a retained key, reads it from the kernel keyring, exports it to PSK interchange format, appends it to a file, and forces mode `0600`.
- `gen_tls_key()` / `check_tls_key()` / `tls_key()` (9912-10382): generate, import, validate, insert, export, revoke, and file-round-trip NVMe/TCP TLS PSK material.
- `show_topology_cmd()` (10384-10460): scans libnvme topology and prints it in requested ranking/order.
- Fabric commands under `CONFIG_FABRICS` (10462-10513): delegate to `fabrics_*()` helpers.
- NVMe-MI commands under `CONFIG_MI` (10515-10656): shared `libnvme_mi()` implementation plus receive/send wrappers.
- Log-page commands (10658-11390): management address list, rotational media info, dispersed namespace participating NVM subsystems, power measurement, reachability groups/associations, host discovery, AVE discovery, and pull-model DDC request logs.
- `register_extension()` (11392-11397): appends external plugin lists to the builtin plugin chain.
- `main()` (11399-11419): initializes extension parentage and locale, installs SIGINT handling, dispatches through `handle_plugin()`, and maps nonzero errors to process exit status `1`.

## Control Flow

The completed passthrough path prints command fields for `--show-command` or dry-run, exits early for dry-run, executes admin or IO passthrough, optionally prints latency, reports completion, and emits read buffers via `passthru_print_read_output()`.

Key commands parse args, create a `libnvme_global_ctx`, validate enum-like parameters, derive/import/export key bytes, optionally insert into the kernel keyring, and optionally update a keyfile. DH-HMAC-CHAP generation appends a little-endian CRC32 before base64 encoding; checking reverses that format and validates length plus CRC.

Most log commands follow parse/open/validate/fetch/show. Variable-length logs first read a header or minimum structure, inspect little-endian length/count fields, grow the buffer, then use specialized log getters or constructed get-log passthrough commands with explicit offsets.

## State And Dependencies

State includes global `nvme_args`, per-command libnvme contexts/transport handles, passthrough config from the pre-chunk half, keyring serial IDs and keyfile contents, reallocatable variable log buffers, and the plugin linked list rooted at `nvme.extensions`.

Dependencies are libnvme, local argument parsing, local print/render helpers, cleanup attributes, base64, CRC32, signal handling, and POSIX file/locale/syscall APIs.

## Risks And Edge Cases

- Several I/O paths check only `read()`/`write() < 0`, not short transfers.
- `check_dhchap_key()` uses `sscanf(..., "DHHC-1:%02x:*s", ...)`, which appears to validate less than intended.
- Some error messages have missing format arguments.
- `import_key()` can leak imported `psk` when key update fails.
- Variable-length log readers trust device-reported counts/lengths for allocation and offset arithmetic.
- `get_log_offset()` sets `args->log` before `libnvme_realloc()`, so a moved allocation can leave a stale data pointer.
- Host discovery, AVE discovery, and pull-model DDC request helpers appear to compute a zero-length second fetch after assigning `log_len` to the reported total.
- `tls_key()` can return from export before restoring `umask`, and can open/truncate a keyfile before validating exactly one action.

## Cross-Chunk References

Pre-chunk lines 9327-9504 define `passthru_print_read_output()` and the first half of `passthru()`. File-scope definitions before this range provide `struct passthru_config`, `nvme_args`, common option strings, and builtin program/plugin state. `nvme-builtin.h` maps command names to these handlers. Output renderers and fabric helper implementations are external to this chunk.
