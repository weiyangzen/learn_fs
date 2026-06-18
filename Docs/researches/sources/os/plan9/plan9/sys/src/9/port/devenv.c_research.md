# File Research: sources/os/plan9/plan9/sys/src/9/port/devenv.c

Implements `#e`, the environment variable filesystem. It serves either the current process environment group (`up->egrp`) or, when attached with spec `c`, the global kernel configuration environment `confegrp`.

`Egrp` entries are managed as `Evalue` records with name, qid, value, and length. Lookup can be by qid path or name. The environment group is read/write locked for enumeration, create, remove, read, write, and truncate.

The namespace is a directory of variable files. Creating a file adds an `Evalue`; opening with `OTRUNC` clears the existing value; reading copies bytes from the stored value; writing extends up to `Maxenvsize` and bumps qid/group versions. Removing deletes the entry.

Configuration environment writes are restricted: `envwriteable` allows `eve` or normal process environment writes, but prevents non-`eve` writes through attached config env. `ksetenv` provides a kernel helper to create/write variables, and `getconfenv` serializes config env as alternating NUL-terminated name/value strings.

`envcpy` deep-copies one environment group to another for process environment inheritance. `closeegrp` releases entries when the refcount drops. Main concerns are version consistency, strict maximum value size, and safe locking around mutable arrays.
