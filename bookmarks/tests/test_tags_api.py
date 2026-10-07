import os

from django.conf import settings
from django.urls import reverse
from rest_framework import status

from bookmarks.models import Bookmark, Tag
from bookmarks.tests.helpers import BookmarkFactoryMixin, LinkdingApiTestCase


class TagsApiTestCase(LinkdingApiTestCase, BookmarkFactoryMixin):
    def test_delete_tag(self):
        self.authenticate()

        tag = self.setup_tag(name="Tag to Delete")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        response = self.delete(url, expected_status_code=status.HTTP_204_NO_CONTENT)

        self.assertEqual(response.content, b"")
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_delete_tag_requires_authentication(self):
        tag = self.setup_tag(name="Protected Tag")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.delete(url, expected_status_code=status.HTTP_401_UNAUTHORIZED)

        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    def test_delete_tag_only_allows_own_tags(self):
        self.authenticate()

        other_user = self.setup_user()
        other_tag = self.setup_tag(name="Other User Tag", user=other_user)
        other_bookmark = self.setup_bookmark(
            user=other_user, tags=[other_tag], title="Other bookmark"
        )

        url = reverse("linkding:tag-detail", kwargs={"pk": other_tag.id})
        self.delete(url, expected_status_code=status.HTTP_404_NOT_FOUND)

        self.assertTrue(Tag.objects.filter(id=other_tag.id).exists())
        other_bookmark.refresh_from_db()
        self.assertCountEqual(list(other_bookmark.tags.all()), [other_tag])

    def test_delete_nonexistent_tag(self):
        self.authenticate()

        url = reverse("linkding:tag-detail", kwargs={"pk": 999999})
        self.delete(url, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_delete_tag_removes_from_list(self):
        self.authenticate()

        tag = self.setup_tag(name="Listed Tag")
        self.setup_tag(name="Other Tag")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.delete(url, expected_status_code=status.HTTP_204_NO_CONTENT)

        list_url = reverse("linkding:tag-list")
        response = self.get(list_url, expected_status_code=status.HTTP_200_OK)

        tag_ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(tag.id, tag_ids)

    def test_delete_tag_makes_detail_unavailable(self):
        self.authenticate()

        tag = self.setup_tag(name="Detail Tag")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.delete(url, expected_status_code=status.HTTP_204_NO_CONTENT)

        self.get(url, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_delete_tag_preserves_bookmarks(self):
        self.authenticate()

        tag_to_delete = self.setup_tag(name="Remove Me")
        keep_tag = self.setup_tag(name="Keep Me")
        bookmark = self.setup_bookmark(tags=[tag_to_delete, keep_tag])

        url = reverse("linkding:tag-detail", kwargs={"pk": tag_to_delete.id})
        self.delete(url, expected_status_code=status.HTTP_204_NO_CONTENT)

        self.assertTrue(Bookmark.objects.filter(id=bookmark.id).exists())
        bookmark.refresh_from_db()
        self.assertCountEqual(list(bookmark.tags.all()), [keep_tag])

    def test_api_docs_describe_tag_delete(self):
        docs_path = os.path.join(
            settings.BASE_DIR, "docs", "src", "content", "docs", "api.md"
        )
        with open(docs_path, encoding="utf-8") as docs_file:
            content = docs_file.read()

        self.assertIn("DELETE /api/tags/<id>/", content)
        self.assertIn("Deletes a tag by ID.", content)
