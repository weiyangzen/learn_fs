# File Research: sources/os/plan9/plan9/sys/src/9/port/devcap.c

Implements `#¤/cap`, a capability device for changing the current process user when a one-shot capability hash is presented. The namespace contains `capuse` for consumers and `caphash` for privileged capability insertion.

Capabilities are stored as SHA1-length hashes in a global `capalloc` list protected by `QLock`. `addcap` appends hashes and trims the list to `Maxhash` entries. `remcap` atomically removes a matching hash, making capabilities single-use.

Only `eve` may open/write `caphash`; `capremove` lets `eve` remove the `caphash` entry from the namespace. Writing at least `SHA1dlen` bytes to `caphash` registers a raw hash.

Writing to `capuse` expects `from[@to]@key`. The driver computes `hmac_sha1(from, key)` and consumes a matching registered hash. If `from@to` form is used, `from` must match `up->user`; the process user becomes `to`. Without an explicit source user, the same field is used as the target user.

This is small but security-sensitive code: authorization depends on one-shot hash secrecy, correct parsing around `@`, and privileged control of `caphash`.
