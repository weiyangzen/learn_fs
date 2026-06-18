# sources/user-network-fs/rclone/cmd/serve/http/http.go

## Purpose

`http.go` implements `rclone serve http`, serving a VFS-backed remote as directory listings, files, ranged downloads, favicon responses, and optional zip archives.

## Important APIs, Types, and Functions

Options are composed from `lib/http` config, auth config, template config, and `DisableZip`. Main APIs are `Command`, `newServer`, `Serve`, `Addr`, `Shutdown`, `getVFS`, `auth`, `serveFavicon`, `handler`, `serveDir`, and `serveFile`.

## Control Flow

Command/RC setup builds either a global VFS or auth-proxy custom auth. `newServer` creates a shared libhttp server, installs compression and headers, and routes favicon, GET, and HEAD requests. Directory requests can stream zip output or render a templated listing. File requests stat a VFS node, set content length/type/Last-Modified, handle HEAD, open the file, account transfer, and use `http.ServeContent` for known-size objects.

## State and Persistence Behavior

The HTTP server stores VFS/proxy/server/options in memory. Served remote content may be read or zipped; this command does not modify content.

## Dependencies and Integration Points

It integrates Cobra, RC, lib/http server/auth/templates, chi middleware, VFS, proxy auth, accounting, embedded favicon data, systemd notification, and generic directory rendering helpers.

## Risks and Test Signals

Risks include auth proxy context value type errors, directory zip resource use, unknown-size range rejection, filter interactions, MIME fallback behavior, and global `vfscommon.Opt.NoModTime` in directory rendering. Tests cover GET/HEAD/POST behavior, hidden filters, ranges, zip golden files, favicon fallback/override, gzip compression, auth proxy, and RC.
