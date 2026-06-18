# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devtab.c

Defines the drawterm kernel device table.

Registered devices, in order:
- `rootdevtab` (`#/`)
- `consdevtab` (`#c`)
- `pipedevtab` (`#|`)
- `ssldevtab` (`#D`)
- `tlsdevtab` (`#a`)
- `mousedevtab` (`#m`)
- `drawdevtab` (`#i`)
- `ipdevtab` (`#I`)
- `fsdevtab` (`#U`)
- `mntdevtab` (`#M`)
- `lfddevtab` (`#L`)
- `audiodevtab` (`#A`)

Role:
- Central dispatch table used by `devno`, `devtab[c->type]`, and namespace/device resolution.
