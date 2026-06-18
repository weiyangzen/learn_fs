# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstored.c

Implements the secstore daemon. It announces by default on `tcp!*!5356`, forks per connection, performs PAK authentication, optionally enforces STA/SecurID, sends `OK`, and then serves commands until `BYE`.

Supported commands are `GET file`, `GET .` for directory listing, `PUT file`, `RM file`, and `CHPASS`. All filenames are passed through `validatefile`, and data is stored under `/adm/secstore/store/<user>/`.

The daemon logs client operations and remote address, has a 30-minute child alarm, supports verbose foreground behavior, custom server name, custom net mount point, and forced STA mode.
