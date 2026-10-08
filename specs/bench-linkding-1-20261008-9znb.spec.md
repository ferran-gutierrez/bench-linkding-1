---
name: Delete tags through the REST API
description: Add authenticated DELETE /api/tags/<id>/ that removes the caller's tag with 204, preserves bookmarks, and document the operation in the API docs.
targets:
  - bookmarks/api/routes.py
  - docs/src/content/docs/api.md
  - bookmarks/tests/test_tags_api.py
---

- **REQ-1** An authenticated `DELETE` request to `/api/tags/<id>/` for a tag owned by the caller removes that tag and responds with `204 No Content` and an empty body.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-2** An unauthenticated `DELETE` request to `/api/tags/<id>/` responds with `401 Unauthorized` and does not remove the tag.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-3** An authenticated `DELETE` request to `/api/tags/<id>/` for a tag owned by another user responds with `404 Not Found` and leaves that tag unchanged in the database.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-4** An authenticated `DELETE` request to `/api/tags/<id>/` for a tag id that does not exist responds with `404 Not Found`.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-5** When a tag is deleted through the API, every bookmark that had that tag remains in the database, no longer references the deleted tag, and still references any other tags it had before deletion.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-6** After a tag is deleted through the API, a `GET` to `/api/tags/` does not include that tag in the results, and a `GET` to `/api/tags/<id>/` for the same id responds with `404 Not Found`.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-7** The API documentation in `docs/src/content/docs/api.md` describes the `DELETE /api/tags/<id>/` operation alongside the existing tag list, retrieve, and create operations.
  `[@test] ../bookmarks/tests/test_tags_api.py`

## Assumptions

- Tag deletion is implemented on `TagViewSet` by adding destroy support consistent with other API view sets (for example `BookmarkBundleViewSet`), using the existing owner-scoped queryset so another user's tag is indistinguishable from a missing id.
- Deleting a tag uses Django's default model deletion, which clears many-to-many relations to bookmarks without deleting bookmark rows; no new service-layer delete helper is required unless the implementation discovers shared side effects.
- API tests for tag deletion live in a new `bookmarks/tests/test_tags_api.py` file using `LinkdingApiTestCase` and `BookmarkFactoryMixin`, matching patterns in `bookmarks/tests/test_bundles_api.py`.
- Documentation verification in REQ-7 is covered by a test that reads `docs/src/content/docs/api.md` and asserts the documented delete path and method, consistent with how other API doc requirements are tested in this project when no dedicated doc test exists yet.
