---
name: Import deduplication by normalized URL
description: Netscape HTML import must treat URLs as equal when their normalized form matches, updating existing owned bookmarks instead of creating duplicates, and skipping later duplicate entries within the same file.
targets:
  - bookmarks/services/importer.py
  - bookmarks/tests/test_importer.py
---

# Import deduplication by normalized URL

Netscape bookmark HTML import must never leave the importing user with two bookmarks for the same URL when those URLs are equivalent under linkding's existing `normalize_url` rules (scheme and host case-insensitive, trailing slashes removed from the path, query parameters sorted).

## Requirements

- **REQ-1** When importing Netscape HTML, an incoming entry matches an existing bookmark owned by the importing user if `normalize_url(entry.href)` equals that bookmark's stored `url_normalized` (or the bookmark's exact `url` when `url_normalized` is empty), even when the raw `href` strings differ.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-2** When an incoming entry matches an existing owned bookmark by normalized URL, the import updates that bookmark with the same field-copy and tag-append behavior used today for an exact URL match on re-import (including `ImportOptions` handling); it must not create a second bookmark row.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-3** When more than one entry in the same import file shares the same normalized URL, only the first entry in file order is imported; every later entry with that normalized URL is skipped without changing title, description, notes, dates, flags, URL, or tags on the bookmark.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-4** Each within-file duplicate skipped under REQ-3 increments `ImportResult.failed`, does not increment `ImportResult.success`, and is still counted in `ImportResult.total` (for example, four parsed entries with two within-file duplicates report total 4, success 2, failed 2).
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-5** Within-file deduplication by normalized URL applies across the entire parsed file, including entries separated by large gaps and entries processed in different import batches, so file order alone determines which occurrence wins.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-6** Bookmarks owned by other users are never selected as the update target for normalized URL matching; a matching URL on another user's account does not prevent creating or updating the importing user's own bookmark.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-7** After a successful import run, the importing user has at most one bookmark per distinct normalized URL among entries that were not skipped as within-file duplicates (no duplicate rows for equivalent URLs such as with/without a trailing slash or permuted query parameters).
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-8** Import behavior unrelated to URL equivalence and within-file deduplication (invalid or missing URLs, tag creation rules, private-flag mapping, archived/notes handling, favicon and preview scheduling, and other existing importer tests) remains unchanged.
  `[@test] ../bookmarks/tests/test_importer.py`

## Assumptions

- URL equivalence for import matching and within-file deduplication uses the existing `normalize_url` implementation in `bookmarks/utils.py` without changing its rules.
- Skipped within-file duplicates are counted as failed import entries via `ImportResult.failed`, consistent with how invalid entries are reported today, rather than as successes or a separate counter.
- When an entry updates an existing bookmark by normalized URL, the stored bookmark `url` may be set to the entry's raw `href` from the file, matching today's behavior when the raw URL strings match exactly.
- Tag names appearing only on skipped duplicate entries are not assigned to the bookmark and are not required to be created solely because a skipped entry referenced them.
