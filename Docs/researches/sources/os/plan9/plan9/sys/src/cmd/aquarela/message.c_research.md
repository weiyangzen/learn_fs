# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/message.c

Constructs NBNS request message objects.

Key functions:
- `nbnsmessagenamequeryrequestnew` creates a query request with one NB question.
- `nbnsmessagenameregistrationrequestnew` creates a registration request with one NB question and an additional NB resource containing flags plus IPv4 address.

Interactions:
- Used by `findname.c` and `addname.c`.
- Uses message allocation/list helpers from `nbnsconv.c`.

Notable details:
- Registration request stores IPv4 in 6-byte rdata: two flag bytes plus four address bytes.
