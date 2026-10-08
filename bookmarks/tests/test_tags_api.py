from pathlib import Path

from django.urls import reverse
from rest_framework import status

from bookmarks.models import Bookmark, Tag
from bookmarks.tests.helpers import BookmarkFactoryMixin, LinkdingApiTestCase

DOCS_API_PATH = Path(__file__).resolve().parents[2] / "docs/src/content/docs/api.md"


class TagsApiTestCase(LinkdingApiTestCase, BookmarkFactoryMixin):
    def test_REQ_1_authenticated_delete_own_tag_returns_204_and_removes_tag(self):
        self.authenticate()

        tag = self.setup_tag(name="tag-to-delete")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        response = self.delete(url, expected_status_code=status.HTTP_204_NO_CONTENT)

        self.assertEqual(response.content, b"")
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_REQ_2_unauthenticated_delete_returns_401_and_preserves_tag(self):
        tag = self.setup_tag(name="protected-tag")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.delete(url, expected_status_code=status.HTTP_401_UNAUTHORIZED)

        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    def test_REQ_3_authenticated_delete_other_users_tag_returns_404(self):
        self.authenticate()

        other_user = self.setup_user()
        other_tag = self.setup_tag(name="other-user-tag", user=other_user)

        url = reverse("linkding:tag-detail", kwargs={"pk": other_tag.id})
        self.delete(url, expected_status_code=status.HTTP_404_NOT_FOUND)

        self.assertTrue(Tag.objects.filter(id=other_tag.id).exists())

    def test_REQ_4_authenticated_delete_nonexistent_tag_returns_404(self):
        self.authenticate()

        url = reverse("linkding:tag-detail", kwargs={"pk": 999999})
        self.delete(url, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_REQ_5_delete_tag_preserves_bookmarks_and_other_tags(self):
        self.authenticate()

        tag_to_delete = self.setup_tag(name="delete-me")
        other_tag = self.setup_tag(name="keep-me")
        bookmark = self.setup_bookmark(tags=[tag_to_delete, other_tag])

        url = reverse("linkding:tag-detail", kwargs={"pk": tag_to_delete.id})
        self.delete(url, expected_status_code=status.HTTP_204_NO_CONTENT)

        self.assertTrue(Bookmark.objects.filter(id=bookmark.id).exists())
        bookmark.refresh_from_db()
        remaining_tag_ids = list(bookmark.tags.values_list("id", flat=True))
        self.assertEqual(remaining_tag_ids, [other_tag.id])
        self.assertFalse(Tag.objects.filter(id=tag_to_delete.id).exists())
        self.assertTrue(Tag.objects.filter(id=other_tag.id).exists())

    def test_REQ_6_after_delete_tag_excluded_from_list_and_detail_returns_404(self):
        self.authenticate()

        tag = self.setup_tag(name="listed-then-deleted")
        self.setup_tag(name="remaining-tag")

        delete_url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.delete(delete_url, expected_status_code=status.HTTP_204_NO_CONTENT)

        list_url = reverse("linkding:tag-list")
        list_response = self.get(list_url, expected_status_code=status.HTTP_200_OK)
        result_ids = [item["id"] for item in list_response.data["results"]]
        self.assertNotIn(tag.id, result_ids)

        detail_url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.get(detail_url, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_REQ_7_api_docs_describe_delete_tags_endpoint(self):
        content = DOCS_API_PATH.read_text(encoding="utf-8")

        self.assertIn("GET /api/tags/", content)
        self.assertIn("GET /api/tags/<id>/", content)
        self.assertIn("POST /api/tags/", content)
        self.assertIn("DELETE /api/tags/<id>/", content)
