# File Research: sources/local-fs/xfsdump/tools/git-contributors.py

## Summary
Python helper that extracts contributor email addresses from git commit logs for a supplied revision spec.

## Main Responsibilities
- Run `git log --pretty=medium <revspec>`.
- Parse trailer-like lines such as `Signed-off-by`, `Acked-by`, `Cc`, `Reviewed-by`, `Reported-by`, `Tested-by`, `Suggested-by`, and `Reported-and-tested-by`.
- Extract email addresses using `email.utils.parseaddr()`.
- Handle some malformed or kernel-style `Cc:` annotations.
- Print a sorted unique address list with a configurable separator.

## Important Behavior
`backtick()` is a generator over subprocess stdout lines.

`find_developers.__init__()` compiles regexes for known tags, comma-separated address detection, and fallback angle-bracket extraction.

`_handle_addr()` strips everything after `#` to work around common kernel stable-CC annotations, uses `parseaddr()`, falls back to text inside angle brackets, and finally returns the raw string.

`run()` scans lines for known tags, splits likely multi-address lines on commas, normalizes each address, and returns `sorted(set(addr_list))`.

`main()` parses `revspec`, `--separator`, and hidden `--debug`, runs the extractor over git log output, prints contributors, and exits zero.

## Dependencies
Depends on Python 3 standard library modules `argparse`, `email.utils`, `io`, `re`, `subprocess`, and `sys`, plus a working `git` executable in the target repository.

## Risks
Comma splitting is heuristic and can mishandle quoted display names containing commas unless the fallback angle-bracket regex saves the address.

`backtick()` does not check the git subprocess return code, so invalid revisions may produce an empty list without a nonzero script exit.

Stripping at `#` can corrupt a technically valid address or display name containing `#`, intentionally favoring common kernel trailer conventions.
