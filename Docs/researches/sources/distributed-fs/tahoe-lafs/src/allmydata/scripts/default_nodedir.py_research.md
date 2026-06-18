# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/default_nodedir.py

## Purpose
Computes the default Tahoe node directory used by CLI commands.

## APIs, Types, And Control Flow
The module exposes `_default_nodedir`. On Windows it asks `allmydata.windows.registry.get_base_dir_path()` and uses that if available; otherwise it expands `~/.tahoe` to an absolute Unicode path. `precondition` assertions verify the result is text.

## State, Persistence, And Integration
No files are written. It integrates with Windows registry support, `abspath_expanduser_unicode`, and `scripts.common.get_default_nodedir`, which propagates the value into CLI option defaults.

## Risks And Test Signals
Import-time platform probing can affect tests and startup behavior. Windows registry failures or unexpected non-string values would fall back or assert. Test signals are CLI basedir tests and Windows fixup/registry tests.
