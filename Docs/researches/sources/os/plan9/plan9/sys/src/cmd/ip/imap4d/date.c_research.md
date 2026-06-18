# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/date.c

Date formatting and parsing for IMAP and RFC 822 mail data. It formats RFC 822 dates, IMAP internal dates, and IMAP date-only strings, and parses IMAP date/time inputs into epoch seconds.

The general parser accepts common mail date forms with optional weekday, month-first or day-first ordering, two- or four-digit years, named RFC 822 zones, military zones, numeric offsets, and local timezone fallback.
