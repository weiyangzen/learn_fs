# File Research: sources/os/plan9/plan9/sys/src/cmd/cal.c

Plan 9 `cal` command. It prints the current month, a specified month, or a full year using Plan 9 `Biobuf` output.

It supports month names/abbreviations via a dictionary in `number`, formats month grids in `cal`, trims output rows in `pstr`, and computes Jan 1 weekdays in `jan1`. The calendar logic includes the 1752 calendar changeover by shortening September and skipping days.

Current month/year come from `localtime(time(0))`. Valid years are 1 through 9999; invalid input prints `cal: bad argument`.
