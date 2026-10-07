---
name: Import deduplication by normalized URL
description: Netscape HTML import must treat URLs equal under normalize_url as one bookmark, update existing user bookmarks on match, and skip later in-file duplicates as failed entries.
targets:
  - bookmarks/services/importer.py
  - bookmarks/tests/test_importer.py
---

# Import deduplication by normalized URL

Netscape HTML import currently matches existing bookmarks by exact URL string, which creates duplicates when the file or library contains equivalent URLs in different forms. Import must use the same URL normalization as the rest of linkding.

## Requirements

- **REQ-1** When importing Netscape HTML, an entry matches an existing bookmark owned by the importing user if `normalize_url(entry.href)` equals that bookmark's normalized URL (including when `url_normalized` was populated from the stored `url` via the same function).
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-2** When an import entry matches an existing bookmark of the importing user by normalized URL, the import updates that bookmark instead of creating a new row, applying the same field and tag-merge behavior as when the entry URL string matches the stored URL exactly today.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-3** When two or more entries in the same import file share the same normalized URL, only the first entry in file order is processed; each later entry is skipped without changing title, description, notes, or other fields and without adding its tags.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-4** Each in-file duplicate skipped under REQ-3 increments `ImportResult.failed`, does not increment `ImportResult.success`, and is still included in `ImportResult.total`; for example four entries with two in-file normalized duplicates report total 4, success 2, failed 2.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-5** Normalized URL matching for import considers only bookmarks owned by the importing user; another user's bookmark with the same normalized URL is never updated or deleted, and the importer still creates or updates only the importing user's bookmark.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-6** In-file normalized-URL deduplication applies across the entire file, including entries separated by more than one import batch size, so a duplicate later in a large file is still skipped as failed.
  `[@test] ../bookmarks/tests/test_importer.py`

## Assumptions

- URL normalization for import deduplication is exclusively `normalize_url` from `bookmarks.utils`, already used when persisting `Bookmark.url_normalized`.
- "First occurrence wins" for in-file duplicates is determined by parser iteration order over the file, regardless of whether an earlier occurrence succeeded or failed.
- Skipped in-file duplicates are counted as failed entries in the import result, consistent with other non-imported entries that do not succeed.
- When updating via normalized match, the stored bookmark `url` is set from the import entry href like today's exact-match update path.
- Bookmarks owned by other users are excluded by scoping lookups to `owner=user` only; no change to global URL uniqueness across users is required.
