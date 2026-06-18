<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/nmfind -->
# sources/user-network-fs/samba/source4/scripting/devel/nmfind

Purpose: shell helper to find object files containing a symbol.

Important APIs/types/functions: positional `TARGET`, object-file arguments, `nm`, and `grep`.

Control flow: shifts off the target, loops over each file, runs `nm` piped to grep, and prints bracketed filenames plus matching symbol lines when found.

State and persistence behavior: read-only inspection of object files.

Dependencies and integration points: developer build debugging helper for compiled Samba objects.

Risks: unquoted `$*` and grep pattern usage can mis-handle spaces or regex metacharacters. It scans serially.

Test signals: printed object filenames and matching `nm` rows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/nmfind -->
