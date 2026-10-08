import os

from django.conf import settings
from django.urls import reverse
from rest_framework import status

from bookmarks.models import Bookmark, Tag
from bookmarks.tests.helpers import BookmarkFactoryMixin, LinkdingApiTestCase


class TagsApiTestCase(LinkdingApiTestCase, BookmarkFactoryMixin):
    def assertTag(self, tag: Tag, data: dict):
        self.assertEqual(tag.id, data["id"])
        self.assertEqual(tag.name, data["name"])
        self.assertEqual(
            tag.date_added.isoformat().replace("+00:00", "Z"), data["date_added"]
        )

    def test_req_1_delete_tag_returns_204_and_removes_tag(self):
        self.authenticate()

        tag = self.setup_tag(name="Tag to Delete")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        response = self.delete(url, expected_status_code=status.HTTP_204_NO_CONTENT)

        self.assertEqual(response.content, b"")
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_req_2_delete_tag_requires_authentication(self):
        tag = self.setup_tag(name="Protected Tag")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.delete(url, expected_status_code=status.HTTP_401_UNAUTHORIZED)

        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    def test_req_3_delete_nonexistent_tag_returns_404(self):
        self.authenticate()

        url = reverse("linkding:tag-detail", kwargs={"pk": 99999})
        self.delete(url, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_req_4_delete_other_users_tag_returns_404_and_leaves_tag(self):
        self.authenticate()

        other_user = self.setup_user()
        other_tag = self.setup_tag(name="Other User Tag", user=other_user)

        url = reverse("linkding:tag-detail", kwargs={"pk": other_tag.id})
        self.delete(url, expected_status_code=status.HTTP_404_NOT_FOUND)

        self.assertTrue(Tag.objects.filter(id=other_tag.id).exists())

    def test_req_5_delete_tag_does_not_delete_bookmarks(self):
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

    def test_req_6_after_delete_tag_missing_from_list_and_detail(self):
        self.authenticate()

        tag = self.setup_tag(name="Listed Tag")
        self.setup_tag(name="Other Tag")

        delete_url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.delete(delete_url, expected_status_code=status.HTTP_204_NO_CONTENT)

        list_url = reverse("linkding:tag-list")
        list_response = self.get(list_url, expected_status_code=status.HTTP_200_OK)
        list_ids = [item["id"] for item in list_response.data["results"]]
        self.assertNotIn(tag.id, list_ids)

        detail_url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.get(detail_url, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_req_7_api_docs_document_tag_delete(self):
        api_doc_path = os.path.join(
            settings.BASE_DIR, "docs", "src", "content", "docs", "api.md"
        )
        with open(api_doc_path, encoding="utf-8") as api_doc:
            content = api_doc.read()

        tags_section_start = content.index("### Tags")
        bundles_section_start = content.index("### Bundles")
        tags_section = content[tags_section_start:bundles_section_start]

        self.assertIn("**Delete**", tags_section)
        self.assertIn("DELETE /api/tags/<id>/", tags_section)
        self.assertIn("204", tags_section)
        self.assertIn("authentication", tags_section.lower())
