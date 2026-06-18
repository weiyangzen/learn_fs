# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/knfs2ganesha-exports.py

## Purpose

`knfs2ganesha-exports.py` converts Linux kernel NFS `/etc/exports` entries from stdin into Ganesha `EXPORT`, `FSAL`, and `CLIENT` configuration blocks.

## Important APIs, Types, and Functions

The pyparsing grammar parses export paths, hosts, and host options. Globals `gan_paths` and `export_id` track generated exports. Functions are `process_exports`, `process_opts`, `create_client`, `usage`, and `main`. Supported FSAL names are `gpfs`, `vfs`, and `lustre`.

## Control Flow

`main` parses optional `--fsal`, creates a temporary config file, sets `CONFFILE`, and calls `process_exports`. Each non-comment stdin line is parsed into a path and host option blocks. `process_opts` maps kernel options to Ganesha key/value pairs and rejects unsupported risky options such as `async` and `subtree_check`. `create_client` shells out to `ganesha_conf set` to create or update blocks. The final temp config is printed to stdout.

## State and Persistence Behavior

The converter writes to a temporary file through `ganesha_conf` and prints generated config. It does not modify `/etc/ganesha/ganesha.conf` unless callers redirect output. Global `export_id` increments per unique path.

## Dependencies and Integration Points

It depends on `pyparsing`, `subprocess`, `tempfile`, and the installed `ganesha_conf` command. It reuses `config_editor` indirectly through that command.

## Risks and Edge Cases

Default options with dash/hyphen are explicitly unsupported. Unknown options abort conversion. Shelling out for every block is slower and inherits `ganesha_conf.py` Python 3 write risks. The parser supports quoted paths but has limited host syntax. Export IDs are generated from input order and may not preserve existing IDs.

## Test Signals

Golden-output tests should feed representative `/etc/exports` lines with `ro/rw`, squash, `sec=`, anon IDs, comments, quoted paths, multiple hosts, unsupported options, and each FSAL. Tests should use a temporary `ganesha_conf` or monkeypatch subprocess.
