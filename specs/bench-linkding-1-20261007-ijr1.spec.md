---
name: REST API tag deletion
description: Add DELETE /api/tags/<id>/ so API clients can remove their own tags without deleting bookmarks, with auth and documentation matching existing tag endpoints.
targets:
  - bookmarks/api/routes.py
  - docs/src/content/docs/api.md
  - bookmarks/tests/test_tags_api.py
---

# REST API tag deletion

## Requirements

- **REQ-1** An authenticated `DELETE` request to `/api/tags/<id>/` for a tag owned by the caller removes that tag and responds with `204 No Content` and an empty body.
  `[@test] ../bookmarks/tests/test_tags_api.py::TagsApiTestCase::test_delete_tag`

- **REQ-2** An unauthenticated `DELETE` request to `/api/tags/<id>/` responds with `401 Unauthorized` and the tag is not deleted.
  `[@test] ../bookmarks/tests/test_tags_api.py::TagsApiTestCase::test_delete_tag_requires_authentication`

- **REQ-3** An authenticated `DELETE` request to `/api/tags/<id>/` for a tag owned by another user responds with `404 Not Found`, leaves that tag unchanged, and does not affect the other user's bookmarks.
  `[@test] ../bookmarks/tests/test_tags_api.py::TagsApiTestCase::test_delete_tag_only_allows_own_tags`

- **REQ-4** An authenticated `DELETE` request to `/api/tags/<id>/` for a tag id that does not exist responds with `404 Not Found`.
  `[@test] ../bookmarks/tests/test_tags_api.py::TagsApiTestCase::test_delete_nonexistent_tag`

- **REQ-5** After a successful tag deletion, `GET /api/tags/` no longer includes that tag.
  `[@test] ../bookmarks/tests/test_tags_api.py::TagsApiTestCase::test_delete_tag_removes_from_list`

- **REQ-6** After a successful tag deletion, `GET /api/tags/<id>/` responds with `404 Not Found`.
  `[@test] ../bookmarks/tests/test_tags_api.py::TagsApiTestCase::test_delete_tag_makes_detail_unavailable`

- **REQ-7** Deleting a tag through the API does not delete any bookmarks; bookmarks that had the tag remain and lose only that tag association while keeping their other tags.
  `[@test] ../bookmarks/tests/test_tags_api.py::TagsApiTestCase::test_delete_tag_preserves_bookmarks`

- **REQ-8** The API documentation in `docs/src/content/docs/api.md` describes the tag delete operation (`DELETE /api/tags/<id>/`) alongside the existing tag list, retrieve, and create operations.
  `[@test] ../bookmarks/tests/test_tags_api.py::TagsApiTestCase::test_api_docs_describe_tag_delete`

## Assumptions

- `TagViewSet` gains delete support by adding `DestroyModelMixin` and using the default `perform_destroy` (model `delete()`), consistent with the web UI tag delete in `bookmarks/views/tags.py` and without a new service function in `bookmarks/services/tags.py`.
- Tag API tests live in a new module `bookmarks/tests/test_tags_api.py` using `LinkdingApiTestCase` and `BookmarkFactoryMixin`, mirroring `bookmarks/tests/test_bundles_api.py`.
- Ownership scoping for delete relies on the existing `get_queryset()` filter (`Tag.objects.filter(owner=user)`), so foreign and missing tags both surface as `404 Not Found` like bundle delete.
- The documentation test verifies that `docs/src/content/docs/api.md` contains the delete endpoint description (same pattern as other doc coverage tests in the project, if any; otherwise a minimal assertion on required doc strings).
