# Research: sources/user-network-fs/rclone/fs/rc/config.go

## sources/user-network-fs/rclone/fs/rc/config.go

Purpose: implements rc endpoints for reading and mutating global and local option blocks without creating an fs package cycle. Registered paths are `options/blocks`, `options/get`, `options/info`, `options/local`, and `options/set`.

Control flow lists `fs.OptionsRegistry`, filters selected block names from an optional comma-separated `blocks` parameter, returns either current option structs or option metadata, returns context-local config/filter state, and writes option blocks via `Reshape`. `options/set` calls a block reload hook when present. State is significant: it mutates global option structs registered in `fs.OptionsRegistry`, while `options/local` reads context-local config/filter values. There is no file persistence here, but changed options can affect later operations process-wide. Dependencies include `fs.OptionsRegistry`, `filter.GetConfig`, and rc reshape utilities. Risks include global mutable state, unknown block errors, silently ignored unknown fields inside known blocks through reshape behavior, reload failure after partial mutation, and exposing internal option field names. Tests cover selection, marshalability, mutation, reload, and errors.
