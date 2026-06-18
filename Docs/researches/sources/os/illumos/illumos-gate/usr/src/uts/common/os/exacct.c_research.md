# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exacct.c

## Purpose

Implements kernel extended accounting record assembly and commit paths for tasks, processes, network link/flow records, and user-supplied accounting tags. It collects usage data, builds libexacct object trees, packs them, and writes them safely to accounting files.

## Main Responsibilities

- Allocates and attaches exacct object items/groups with `ea_alloc_item()`, `ea_alloc_group()`, and `ea_attach_item()`.
- Creates exacct file headers with `exacct_create_header()` and writes them with `exacct_write_header()`.
- Safely appends packed records to accounting vnodes with rollback-on-error behavior.
- Computes task usage for final, partial, and interval records.
- Computes process usage for final and partial records.
- Assembles and commits network link, network flow, and legacy flow records.
- Implements `putacct(2)` tagging support for tasks and processes.
- Initializes exacct cache/taskq state with `exacct_init()`.
- Accounts for process movement between tasks with `exacct_move_mstate()`.

## Key Data and Globals

- `exacct_queue`: uses `system_taskq` for deferred accounting work.
- `exacct_object_cache`: kmem cache for `ea_object_t`.
- `exacct_zone_key`: zone-specific accounting globals key, initialized by acctctl outside this file.
- `exacct_version`, `exacct_header`, `exacct_creator`: static file header fields.

## File Write Safety

- `exacct_vn_write_impl()` requires `ac_lock`, reads current vnode size, appends via `vn_rdwr(FAPPEND)`, and restores the previous size on write error or short write.
- `exacct_vn_write()` skips inactive/null accounting files and serializes each accounting file through `ac_lock`.
- `exacct_commit_callback()` is the standard callback used by record assemblers to write packed buffers.

## Task Accounting Flow

- `exacct_update_task_mstate()` adds exiting process microstate/resource counters into its task aggregate.
- `exacct_snapshot_task_usage()` walks current task members under `pidlock`, adds approximate live-process usage, subtracts inherited usage, and stamps finish time.
- `exacct_get_interval_task_usage()` subtracts previous interval usage and updates either zone-local or global previous-usage storage.
- `exacct_calculate_task_usage()` chooses final, partial, or interval calculation rules.
- `exacct_attach_task_item()` maps selected `AC_TASK_*` resources into exacct catalog items.
- `exacct_assemble_task_usage()` copies the active resource mask, builds a task group (`TASK`, `TASK_PARTIAL`, or `TASK_INTERVAL`), packs it, and invokes the supplied callback.
- `exacct_commit_task()` writes final task records for the task’s zone and, for non-global zones, also for the global zone, then calls `task_end()`.

## Process Accounting Flow

- `exacct_calculate_proc_usage()` runs under `p_lock`, computes CPU and time fields, identifiers, terminal device, wait status, credentials, command, zone name, nodename, memory RSS average/max, and microstate counters.
- Partial records aggregate live LWP counters with `exacct_calculate_proc_mstate()`.
- Final records copy already accumulated process resource counters with `exacct_copy_proc_mstate()`.
- `exacct_attach_proc_item()` maps `AC_PROC_*` resources into exacct catalog items.
- `exacct_assemble_proc_usage()` builds `PROC` or `PROC_PARTIAL` groups based on the active process mask.
- `exacct_commit_proc()` commits final process records for the process zone and, for non-global zones, also for the global zone.

## Network and Flow Accounting

- `exacct_attach_netstat_item()` records link/flow statistics such as bytes, packets, and error packets.
- `exacct_attach_netdesc_item()` records descriptors such as link/device names, Ethernet addresses, VLAN fields, SAP, priority, bandwidth limit, IP addresses, ports, protocol, and DS field.
- `exacct_assemble_net_usage()` builds one of `NET_LINK_DESC`, `NET_LINK_STATS`, `NET_FLOW_DESC`, or `NET_FLOW_STATS`.
- `exacct_commit_netinfo()` uses global-zone network accounting settings.
- `exacct_attach_flow_item()` records legacy flow attributes: addresses, ports, protocol, DS field, creation/last-seen time, bytes, packets, project id, uid, and action name.
- `exacct_assemble_flow_usage()` builds an `EXD_GROUP_FLOW` record.
- `exacct_commit_flow()` commits legacy flow usage through global-zone flow accounting settings.

## Tagging Support

- `exacct_tag_task()` builds a task tag group with task id, hostname, and caller-supplied raw or exacct-object payload.
- `exacct_tag_proc()` builds a process tag group with pid, task id, hostname, and caller-supplied payload.
- Both return `ENOTACTIVE` if the accounting file is off or missing.

## Task Movement Accounting

- `exacct_snapshot_proc_mstate()` snapshots a process’s current user/system time and resource counters into `task_usage_t`.
- `exacct_move_mstate()` is called during task changes with `pidlock` and `p_lock` already held; it adds the process snapshot to the old task’s aggregate and to the new task’s inherited usage so accounting excludes pre-move consumption from the new task.

## External Interfaces and Dependencies

- Exported/accounting-facing functions include `exacct_create_header()`, `exacct_write_header()`, `exacct_update_task_mstate()`, `exacct_assemble_task_usage()`, `exacct_commit_task()`, `exacct_calculate_proc_usage()`, `exacct_assemble_proc_usage()`, `exacct_commit_callback()`, `exacct_commit_proc()`, `exacct_assemble_net_usage()`, `exacct_commit_netinfo()`, `exacct_assemble_flow_usage()`, `exacct_commit_flow()`, `exacct_tag_task()`, `exacct_tag_proc()`, `exacct_init()`, and `exacct_move_mstate()`.
- Depends on tasks/projects/zones, process and LWP resource accounting, vnode writes, acctctl state, bitmap masks, libexacct packing, microstate accounting, and network/flow accounting structures.

## Notable Edge Cases

- If a selected resource mask produces an empty record, assembly returns success without writing.
- If acctctl is not loaded (`exacct_zone_key == ZONE_KEY_UNINITIALIZED`) or zone-specific globals are unavailable during zone teardown, commit paths skip work.
- Network and flow accounting currently use global-zone settings even though comments note nominal per-zone flow settings.
- Header creation zeroes the final backskip so reverse readers do not treat the file header as a normal trailing record.
