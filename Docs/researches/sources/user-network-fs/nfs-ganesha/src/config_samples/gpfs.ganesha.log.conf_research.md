# sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.log.conf

## Purpose

`gpfs.ganesha.log.conf` is the logging fragment for the split GPFS sample configuration.

## Important APIs, Types, and Functions

It defines a `LOG` block with `Default_log_level`, nested `Facility`, `Format`, and `Components` subblocks. Facility fields include `name`, `destination`, `max_level`, `headers`, and `enable`.

## Control Flow

The sample configures default log level `EVENT`, a file facility at `/var/log/ganesha/nfs-ganesha.log` with full-debug maximum, detailed ISO-8601 formatting fields, and component level `ALL = EVENT`.

## State and Persistence Behavior

At runtime it writes logs to the configured destination and controls log verbosity/format. It does not affect parser state beyond normal block loading.

## Dependencies and Integration Points

It integrates with Ganesha's logging configuration loader, file facility backend, and component-level filtering.

## Risks and Edge Cases

The destination directory must exist and be writable by the daemon. `max_level = FULL_DEBUG` can permit high-volume logging if enabled, though component default remains `EVENT`.

## Test Signals

Syntax validation should pass, and runtime tests should confirm log file creation, selected headers/format fields, and component level behavior.
