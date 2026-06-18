# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/info.c

Defines the synthetic info directory entries exposed by the CIFS mount. `Infdir` maps names such as `Users`, `Groups`, `Shares`, `Connection`, `Sessions`, `Dfsroot`, `Dfscache`, `Domains`, `Openfiles`, `Workstations`, and `Filetable` to generator functions.

`walkinfo` resolves a top-level info filename to its slot. `numinfo` reports the number of info entries. `dirgeninfo` fills a Plan 9 `Dir` for an info file using `mkqid`.

`makeinfo` lazily materializes an info file by running its generator into a string buffer. `readinfo` serves slices from that cached buffer. `freeinfo` releases the cached buffer when the fid is destroyed.

The file is the bridge between 9P directory walking in `main.c` and the live server-reporting functions in `fs.c`.

Boundary note: range checks use `path > nelem(Infdir)` rather than `>=`, which means `path == nelem(Infdir)` passes in several functions and would index past the table if reached.
