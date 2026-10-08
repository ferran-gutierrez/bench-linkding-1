---
name: REST API tag deletion
description: Add DELETE /api/tags/<id>/ so API clients can remove their tags without removing bookmarks, with auth and ownership rules matching other tag endpoints.
targets:
  - bookmarks/api/routes.py
  - docs/src/content/docs/api.md
  - bookmarks/tests/test_tags_api.py
---

# REST API tag deletion

## Requirements

- **REQ-1** An authenticated `DELETE` request to `/api/tags/<id>/` for a tag owned by the caller removes that tag and responds with `204 No Content` and an empty body.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-2** A `DELETE` request to `/api/tags/<id>/` without valid API token authentication responds with `401 Unauthorized` and does not delete the tag.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-3** An authenticated `DELETE` for a tag ID that does not exist responds with `404 Not Found`.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-4** An authenticated `DELETE` for a tag owned by another user responds with `404 Not Found` and leaves that tag unchanged in the database.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-5** Deleting a tag via the API does not delete any bookmarks; bookmarks that had the tag remain, no longer include the deleted tag, and keep their other tags.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-6** After a successful API tag deletion, the tag is omitted from `GET /api/tags/` and `GET /api/tags/<id>/` returns `404 Not Found`.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-7** The public API documentation under Tags documents the delete operation (`DELETE /api/tags/<id>/`, success `204`, auth required) alongside list, retrieve, and create.
  `[@test] ../bookmarks/tests/test_tags_api.py`

## Assumptions

- Ownership and not-found handling for delete match existing tag list/retrieve and bundle delete: the viewset queryset is scoped to the authenticated user, so another user's tag and a missing ID both yield `404 Not Found`.
- Tag removal uses the standard model delete (as in the tags UI); Django clears the bookmark–tag many-to-many link without deleting bookmark rows.
- No tag-specific `perform_destroy` service hook is required (unlike bundles); adding `DestroyModelMixin` to `TagViewSet` is sufficient unless tests reveal missing cleanup.
