# File Research: sources/os/linux/linux/block/blk-cgroup-fc-appid.c

## Scope

This small file provides Fibre Channel application-id storage and lookup on block cgroups when `CONFIG_BLK_CGROUP_FC_APPID` is enabled.

## Core APIs

- `blkcg_set_fc_appid()` sets `blkcg->fc_app_id` for a cgroup identified by numeric cgroup id.
- `blkcg_get_fc_appid()` returns the application id associated with a bio’s `bi_blkg`, or `NULL` if none exists.

## Control Flow

- `blkcg_set_fc_appid()` validates `app_id_len <= FC_APPID_LEN`, obtains the cgroup by id, obtains the io controller css with `cgroup_get_e_css()`, converts it to `struct blkcg`, and stores the string with `strscpy()`.
- `blkcg_get_fc_appid()` requires a bio blkcg association and a nonempty `fc_app_id`.

## Dependencies

- `blk-cgroup.h` for `struct blkcg`, `css_to_blkcg()`, and `io_cgrp_subsys`.
- Cgroup reference APIs: `cgroup_get_from_id()`, `cgroup_get_e_css()`, `css_put()`, `cgroup_put()`.

## Risks and Invariants

- Setting the app id is intentionally lockless. The comment accepts a small race where an I/O may observe no id or an older id.
- The length check rejects values larger than `FC_APPID_LEN`, but callers must still provide a sensible string buffer for `strscpy()`.
