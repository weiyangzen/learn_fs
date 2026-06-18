# sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/ganesha-top.py

## Purpose
`ganesha-top.py` is an interactive curses dashboard for a running `ganesha.nfsd`. It enables stats, samples process memory/CPU through `psutil`, queries DBus management/statistics interfaces, and displays version, export, client, cache, and NFSv4 operation data.

## Important APIs, Types, And Functions
The CLI accepts `-i/--interval`. Constants define the process/service names and refresh defaults. `enbale_all_stats`, `get_ganesha_pid`, `setup_color`, `convert_memory_size`, and `generate_version` provide utilities. `SingleTon` supplies one-instance behavior. `ClientInterface` and `ExportInterface` bind DBus methods. `ClientMgr`, `ExportMgr`, and `GaneshaPSInfo` cache/process DBus and process data. Drawing functions render header, footer, default NFSv4 detail page, client page, export page, and help page.

## Control Flow
`main` parses interval, checks for `ganesha.nfsd`, enables all stats, and enters `curses.wrapper(draw_menu, interval)`. `draw_menu` initializes colors and loops until `q`, redrawing the selected page based on `h`, `c`, `d`, or `e`. Pages clear the screen, gather live data through managers, draw fixed-position header content, render page rows, and draw the footer.

## State And Persistence
The tool writes no files. Runtime state lives in singleton instances and dictionaries for clients, exports, global ops, cache info, v4 details, and process info. It changes live server behavior by invoking `ganesha_stats enable all`.

## Dependencies And Integration Points
Dependencies are `curses`, `argparse`, `subprocess`, `datetime`, `psutil`, `dbus`, `pidof`, `ganesha_stats`, and in-tree modules `Ganesha.ganesha_mgr_utils` and `Ganesha.glib_dbus_stats`. It requires system DBus access to `org.ganesha.nfsd` and a running Ganesha daemon.

## Risks And Edge Cases
`subprocess.run` is used without `check=True`, so command failures are not caught as intended; empty `pidof` output can raise `ValueError`. Fixed-position `curses.addstr` calls can fail on narrow terminals. DBus parsing uses fragile positional indexes. Singleton initialization can repeatedly reset data while still sharing instances. `memory_full_info().swap` may not be available everywhere. There is no broad exception boundary around DBus or drawing failures.

## Test Signals
Run `python3 -m py_compile` with the proper module path. Unit-test DBus parsing and drawing with mocks. Integration-test against a DBus-enabled Ganesha instance and exercise `d`, `c`, `e`, `h`, and `q`. Include tests for failed `pidof`/`ganesha_stats` and narrow terminals.
